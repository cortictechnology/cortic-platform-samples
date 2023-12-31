""" 
COPYRIGHT_NOTICE:
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2022-2023
COPYRIGHT_NOTICE
"""

import os
import json
import time
from argparse import ArgumentParser
import service_main
import logging
import threading
import traceback
import copy
import cv2
import numpy as np
import base64
from collections import deque
from multiprocessing.connection import Client
from cortic_logger import CorticLogger
import sys
from contextlib import redirect_stdout, redirect_stderr
from cortic_platform.sdk.service import ServiceStatus
from cortic_platform.sdk.service_data_types import ServiceDataTypes
from cortic_platform.sdk.logging import log, LogLevel

real_stdout = sys.stdout
real_stderr = sys.stderr

stop_service = False
pause_service = False
activate_service = False
task_queue = None
dm_conn = None
dm_conn_sender = None
dm_conn_lock = threading.Lock()
this_service = None
sent_historical_log = False
historical_log = ""
alive_time_check_period = 5

dm_process_last_alive_time = None

logging.basicConfig(stream=real_stdout, level=logging.INFO)


def task_func():
    global dm_conn
    global task_queue
    while not stop_service:
        try:
            msg = dm_conn.recv()
            if "task_data" in msg:
                task_queue.append(copy.deepcopy(msg["task_data"]))
            msg = None
        except Exception as e:
            log("error: " + str(traceback.format_exc()), LogLevel.Error)
            print(msg)
            log("Received corrupted data, throwing away..", LogLevel.Error)
            continue


def communication_func():
    global dm_conn
    global dm_conn_lock
    global dm_conn_sender
    global this_service
    global stop_service
    global pause_service
    global activate_service
    global task_queue
    global dm_process_last_alive_time
    while not stop_service:
        try:
            msg = dm_conn_sender.recv()
            dm_process_last_alive_time = time.time()
            if "activate" in msg:
                activate_service = msg["activate"]
            elif "set_states" in msg:
                if this_service is not None:
                    states = msg["set_states"]["states"]
                    for state_name in states:
                        this_service.context._set_state(msg["set_states"]["hub"],
                                                        msg["set_states"]["app"],
                                                        msg["set_states"]["pipeline"],
                                                        state_name,
                                                        states[state_name])
            elif "get_states" in msg:
                if this_service is not None:
                    states = this_service.context.states
                    for key in list(states.keys()):
                        # Not supporting numpy arrays for now as they are not json serializable
                        if isinstance(states[key], np.ndarray):
                            del states[key]
                    
                    dm_conn_sender.send("service_states", states)
                    
            elif "reset_states" in msg:
                if this_service is not None:
                    this_service.context._reset_states(msg["reset_states"]["hub"],
                                                       msg["reset_states"]["app"],
                                                       msg["reset_states"]["pipeline"])
            elif "restore_states" in msg:
                if this_service is not None:
                    this_service.context.states = msg["restore_states"]
            elif "clear_states" in msg:
                if this_service is not None:
                    this_service.context.clear_states()
            elif "stop_service" in msg:
                stop_service = True
            elif "pause_service" in msg:
                pause_service = True
            elif "resume_service" in msg:
                pause_service = False
            elif "ping" in msg:
                dm_conn_sender.send("pong")
            msg = None
        except Exception as e:
            log("error: " + str(traceback.format_exc()), LogLevel.Error)
            print(msg)
            log("Received corrupted data, throwing away..", LogLevel.Error)
            continue


def alive_func():
    global stop_service
    global dm_process_last_alive_time
    global alive_time_check_period
    while not stop_service:
        if (time.time() - dm_process_last_alive_time) > 3 * alive_time_check_period:
            log("Device manager process is not alive", LogLevel.Error)
            stop_service = True
        time.sleep(alive_time_check_period / 2)


def log_callback(log):
    global this_service
    global dm_conn
    global dm_conn_lock
    global dm_conn_sender
    global historical_log
    global sent_historical_log
    if dm_conn_sender is not None:
        if not sent_historical_log:
            historical_log = historical_log + log
            dm_conn_sender.send({"cortic_service_log": historical_log})
            historical_log = ""
            sent_historical_log = True
        else:
            dm_conn_sender.send({"cortic_service_log": log})
            
    else:
        historical_log = historical_log + log


def main(
    service_name,
    processing_queue_size,
    processing_fps,
    listener_ip,
    listener_port,
    sender_ip,
    sender_port,
    auth_key,
):
    global this_service
    global dm_conn
    global dm_conn_lock
    global dm_conn_sender
    global stop_service
    global pause_service
    global activate_service
    global task_queue
    global dm_process_last_alive_time

    fatal_error = False
    task_queue = deque(maxlen=processing_queue_size)
    with open(os.path.dirname(os.path.realpath(__file__)) + "/manifest.json") as f:
        service_config = json.loads(f.read())
    service_class_name = service_config["service_class"]
    service = getattr(service_main, service_class_name)
    try:
        this_service = service()
    except Exception as e:
        log(
            "Failed to initialize service class, error: " + str(traceback.format_exc()),
            LogLevel.Error,
        )
        
        fatal_error = True
    this_service.config = service_config
    is_data_source = service_config["is_data_source"]
    # is_data_source = False
    # if len(this_service.input_type) == 0:
    #     is_data_source = True
    # else:
    #     is_data_source = True
    #     for input_name in this_service.input_type:
    #         if isinstance(this_service.input_type[input_name], dict):
    #             is_data_source = False
    #             break
    if not isinstance(this_service.input_type, dict):
        log(
            service_class_name + " , input type must be a dictionary",
            LogLevel.Error,
        )
        fatal_error = True
    for input_name in this_service.input_type:
        if fatal_error:
            break
        if not isinstance(input_name, str):
            log(service_class_name + " , input name must be a string", LogLevel.Error)
            fatal_error = True
            break

        if not isinstance(this_service.input_type[input_name], dict) and not isinstance(
            this_service.input_type[input_name], ServiceDataTypes
        ):
            log(
                service_class_name
                + " , input specification of an input name must be a dictionary or a ServiceDataTypes",
                LogLevel.Error,
            )
            fatal_error = True
            break

        if isinstance(this_service.input_type[input_name], dict):
            for input_data_name in this_service.input_type[input_name]:
                if not isinstance(input_data_name, str):
                    log(
                        service_class_name
                        + " , input map of a specific input name must be a dictionary with keys of type str",
                        LogLevel.Error,
                    )
                    fatal_error = True
                    break
                if not isinstance(
                    this_service.input_type[input_name][input_data_name],
                    ServiceDataTypes,
                ):
                    log(
                        service_class_name
                        + " , Input map of a specific input name must be a dictionary with values of type ServiceDataTypes",
                        LogLevel.Error,
                    )
                    log(
                        service_class_name
                        + " with input name "
                        + input_name
                        + " and input data name "
                        + input_data_name
                        + " has invalid input type "
                        + str(this_service.input_type[input_name][input_data_name]),
                        LogLevel.Error,
                    )
                    fatal_error = True
                    break
    if not isinstance(this_service.output_type, dict):
        log(service_class_name + ", output type must be a dictionary")
        fatal_error = True
    for output_name in this_service.output_type:
        if fatal_error:
            break
        if not isinstance(output_name, str):
            log(service_class_name + " , output name must be a string", LogLevel.Error)
            fatal_error = True
        if not isinstance(this_service.output_type[output_name], ServiceDataTypes):
            log(
                service_class_name
                + ", output type must be a dictionary with values of type ServiceDataTypes",
                LogLevel.Error,
            )
            log(
                service_class_name
                + " with output name "
                + output_name
                + " has invalid output type "
                + str(this_service.output_type[output_name]),
                LogLevel.Error,
            )
            fatal_error = True
            break

    address = (listener_ip, listener_port)
    dm_conn = Client(address, authkey=str.encode(auth_key))
    task_thread = threading.Thread(target=task_func, daemon=True)
    task_thread.start()
    dm_conn_sender = Client((sender_ip, sender_port),
                            authkey=str.encode(auth_key))
    dm_process_last_alive_time = time.time()
    communication_thread = threading.Thread(
        target=communication_func, daemon=True)
    communication_thread.start()

    alive_thread = threading.Thread(target=alive_func, daemon=True)
    alive_thread.start()
    log_callback("")
    # Quit after sending fatal error log
    if fatal_error:
        return

    log(service_name + " is initialized")
    this_service.context._dm_connection = dm_conn_sender
    
    dm_conn_sender.send(
        {
            "status": "Activated",
            "input_type": json.dumps(this_service.input_type),
            "output_type": json.dumps(this_service.output_type),
            "service_states": json.dumps(this_service.context._default_states)
        }
    )
    
    while not stop_service:
        if activate_service:
            if this_service.status != ServiceStatus.Activated:
                try:
                    log("Activating " + service_name + "...")
                    this_service.activate()
                    this_service.status = ServiceStatus.Activated
                    
                    dm_conn_sender.send({"status": "Idle"})
                    
                except Exception:
                    this_service.status = ServiceStatus.Deactivated
                    logging.error(traceback.format_exc())
                    
                    dm_conn_sender.send(
                        {
                            "exception": {
                                "type": "service",
                                "name": service_name,
                                "exception_message": "Activate service error",
                                "traceback": traceback.format_exc(),
                            }
                        }
                    )
                    
            # if len(task_queue) > 0:
            if len(task_queue) > 0:
                task_data = task_queue.popleft()
                if task_data:
                    self_guid = task_data["self_guid"]
                    hub = task_data["hub"]
                    app = task_data["app"]
                    pipeline = task_data["pipeline"]
                    try:
                        start_time = time.time()
                        load = len(task_queue)
                        if is_data_source:
                            load = 0
                            app = "*"
                            pipeline = "*"
                            if self_guid != "for_pipeline":
                                app = task_data["app"]
                        peer_names = []
                        for input_name in task_data["data"]:
                            data = task_data["data"][input_name]
                            if isinstance(data, dict) and this_service.input_type[input_name] != ServiceDataTypes.Json:
                                for data_name in data:
                                    if data_name == "peer_names":
                                        peer_names = peer_names + \
                                            data["peer_names"]
                                    else:
                                        if data_name in this_service.input_type[input_name]:
                                            if (
                                                this_service.input_type[input_name][
                                                    data_name
                                                ]
                                                == ServiceDataTypes.CvFrame
                                            ):
                                                imgdata = base64.b64decode(
                                                    data[data_name])
                                                task_data["data"][input_name][
                                                    data_name
                                                ] = cv2.imdecode(
                                                    np.frombuffer(
                                                        imgdata, np.uint8),
                                                    flags=1,
                                                )
                                            elif (
                                                this_service.input_type[input_name][
                                                    data_name
                                                ]
                                                == ServiceDataTypes.NumpyArray
                                            ):
                                                task_data["data"][input_name][
                                                    data_name
                                                ] = np.array(data[data_name])
                            else:
                                if (
                                    this_service.input_type[input_name]
                                    == ServiceDataTypes.CvFrame
                                ):
                                    imgdata = base64.b64decode(data)
                                    task_data["data"][input_name] = cv2.imdecode(
                                        np.frombuffer(imgdata, np.uint8), flags=1
                                    )
                                elif (
                                    this_service.input_type[input_name]
                                    == ServiceDataTypes.NumpyArray
                                ):
                                    task_data["data"][input_name] = np.array(
                                        data)
                        this_service._current_task_source_hub = hub
                        this_service._current_task_source_app = app
                        this_service._current_task_source_pipeline = pipeline
                        result_data = this_service.process(task_data["data"])
                        if not isinstance(result_data, dict):
                            log(
                                "Output data must be a dictionary, ignoring this data",
                                LogLevel.Warning,
                            )
                            continue
                        for data_name in result_data:
                            if not isinstance(data_name, str):
                                log(
                                    "Output data must be a dictionary with string keys, ignoring this data",
                                    LogLevel.Warning,
                                )
                                continue
                            if data_name not in this_service.output_type:
                                log(
                                    "data name: "
                                    + data_name
                                    + "not found in output type, ignoring this data",
                                    LogLevel.Warning,
                                )
                                continue
                            if (
                                this_service.output_type[data_name]
                                == ServiceDataTypes.CvFrame
                            ):
                                if not isinstance(result_data[data_name], np.ndarray):
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not a CvFrame, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                                else:
                                    encode_param = [
                                        int(cv2.IMWRITE_JPEG_QUALITY), service_config["image_compress_quality"]]
                                    _, buffer = cv2.imencode(
                                        ".jpg", result_data[data_name], encode_param
                                    )
                                    imgByteArr = base64.b64encode(buffer)
                                    result_data[data_name] = imgByteArr.decode(
                                        "ascii")
                            elif (
                                this_service.output_type[data_name]
                                == ServiceDataTypes.NumpyArray
                            ):
                                if not isinstance(result_data[data_name], np.ndarray):
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not a NumpyArray, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                                else:
                                    result_data[data_name] = result_data[data_name].tolist(
                                    )
                            elif (
                                this_service.output_type[data_name]
                                == ServiceDataTypes.String
                            ):
                                if not isinstance(result_data[data_name], str):
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not a String, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                            elif (
                                this_service.output_type[data_name]
                                == ServiceDataTypes.Int
                            ):
                                if not isinstance(result_data[data_name], int):
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not a Int, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                            elif (
                                this_service.output_type[data_name]
                                == ServiceDataTypes.Float
                            ):
                                if not isinstance(result_data[data_name], float):
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not a Float, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                            elif (
                                this_service.output_type[data_name]
                                == ServiceDataTypes.Boolean
                            ):
                                if not isinstance(result_data[data_name], bool):
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not a Boolean, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                            elif (
                                this_service.output_type[data_name]
                                == ServiceDataTypes.List
                            ):
                                if not isinstance(result_data[data_name], list):
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not a List, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                                serializable = True
                                try:
                                    json.dumps(result_data[data_name])
                                except:
                                    serializable = False
                                if not serializable:
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not serializable, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                            elif (
                                this_service.output_type[data_name]
                                == ServiceDataTypes.Json
                            ):
                                if not isinstance(result_data[data_name], dict):
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not a Dict, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                                serializable = True
                                try:
                                    json.dumps(result_data[data_name])
                                except:
                                    serializable = False
                                if not serializable:
                                    result_data[data_name] = None
                                    log(
                                        "Exception occured! Output data of "
                                        + data_name
                                        + " is not serializable, replaced data with None. Please check your service code.",
                                        LogLevel.Error,
                                    )
                        result_msg = {
                            "task_result": {
                                "self_guid": self_guid,
                                "result": result_data,
                                "app": app,
                                "pipeline": pipeline,
                                "processing_queue_size": load,
                                "for_pipeline": task_data["for_pipeline"],
                                "stateful": len(this_service.context.states) > 0,
                            }
                        }
                        if len(peer_names) > 0:
                            result_msg = {
                                "task_result": {
                                    "self_guid": self_guid,
                                    "result": result_data,
                                    "app": app,
                                    "pipeline": pipeline,
                                    "processing_queue_size": load,
                                    "peer_names": peer_names,
                                    "for_pipeline": task_data["for_pipeline"],
                                    "stateful": len(this_service.context.states) > 0,
                                }
                            }
                        
                        dm_conn_sender.send(json.dumps(result_msg))
                        

                        remaining_time = 1.0 / processing_fps - (
                            time.time() - start_time
                        )
                        if remaining_time > 0:
                            time.sleep(remaining_time)

                    except Exception as e:
                        log(
                            "Exception: "
                            + str(e)
                            + " in "
                            + service_name,
                            LogLevel.Error,
                        )
                        print(traceback.format_exc())
                        
                        dm_conn_sender.send(
                            {
                                "task_result": {
                                    "self_guid": self_guid,
                                    "result": {
                                        "exception": {
                                            "type": "task",
                                            "name": service_name,
                                            "processing_queue_size": len(task_queue),
                                            "exception_message": "Processing error",
                                            "traceback": traceback.format_exc(),
                                        }
                                    },
                                    "stateful": len(this_service.context.states) > 0,
                                }
                            }
                        )
                        

            else:
                if (
                    is_data_source and not pause_service
                ):  # not required to receive data, service is a data source
                    start_time = time.time()
                    data = {}
                    for input_name in this_service.input_type:
                        data[input_name] = None
                    result_data = this_service.process(data)
                    for data_name in result_data:
                        if (
                            this_service.output_type[data_name]
                            == ServiceDataTypes.CvFrame
                        ):
                            if not isinstance(result_data[data_name], np.ndarray):
                                result_data[data_name] = None
                                log(
                                    "Exception occured! Output data of "
                                    + data_name
                                    + " is not a CvFrame, replaced data with None. Please check your service code.",
                                    LogLevel.Error,
                                )
                            else:
                                encode_param = [
                                    int(cv2.IMWRITE_JPEG_QUALITY), service_config["image_compress_quality"]]
                                _, buffer = cv2.imencode(
                                    ".jpg", result_data[data_name], encode_param
                                )
                                imgByteArr = base64.b64encode(buffer)
                                result_data[data_name] = imgByteArr.decode(
                                    "ascii")
                        elif (
                            this_service.output_type[data_name]
                            == ServiceDataTypes.NumpyArray
                        ):
                            if not isinstance(result_data[data_name], np.ndarray):
                                result_data[data_name] = None
                                log(
                                    "Exception occured! Output data of "
                                    + data_name
                                    + " is not a NumpyArray, replaced data with None. Please check your service code.",
                                    LogLevel.Error,
                                )
                            else:
                                result_data[data_name] = result_data[data_name].tolist(
                                )
                        elif (
                            this_service.output_type[data_name]
                            == ServiceDataTypes.List
                        ):
                            if not isinstance(result_data[data_name], list):
                                result_data[data_name] = None
                                log(
                                    "Exception occured! Output data of "
                                    + data_name
                                    + " is not a List, replaced data with None. Please check your service code.",
                                    LogLevel.Error,
                                )
                            serializable = True
                            try:
                                json.dumps(result_data[data_name])
                            except:
                                serializable = False
                            if not serializable:
                                result_data[data_name] = None
                                log(
                                    "Exception occured! Output data of "
                                    + data_name
                                    + " is not serializable, replaced data with None. Please check your service code.",
                                    LogLevel.Error,
                                )
                        elif (
                            this_service.output_type[data_name]
                            == ServiceDataTypes.Json
                        ):
                            if not isinstance(result_data[data_name], dict):
                                result_data[data_name] = None
                                log(
                                    "Exception occured! Output data of "
                                    + data_name
                                    + " is not a Dict, replaced data with None. Please check your service code.",
                                    LogLevel.Error,
                                )
                            serializable = True
                            try:
                                json.dumps(result_data[data_name])
                            except:
                                serializable = False
                            if not serializable:
                                result_data[data_name] = None
                                log(
                                    "Exception occured! Output data of "
                                    + data_name
                                    + " is not serializable, replaced data with None. Please check your service code.",
                                    LogLevel.Error,
                                )
                    
                    dm_conn_sender.send(
                        json.dumps({
                            "task_result": {
                                "self_guid": "for_pipeline",
                                "result": result_data,
                                "app": "*",
                                "pipeline": "*",
                                "processing_queue_size": 0,
                                "for_pipeline": True,
                                "stateful": len(this_service.context.states) > 0,
                            }
                        })
                    )
                    
                    remaining_time = 1.0 / processing_fps - \
                        (time.time() - start_time)
                    if remaining_time > 0:
                        time.sleep(remaining_time)
                else:
                    time.sleep(0.005)
        else:
            if this_service.status == ServiceStatus.Activated:
                log("Deactivating " + service_name + "...")
                this_service.deactivate()
                this_service.status = ServiceStatus.Deactivated
                
                dm_conn_sender.send({"status": "Activated"})
                
            else:
                time.sleep(1)
    log("Stopping service")
    if this_service.status == ServiceStatus.Activated:
        log("Deactivating " + service_name + "...")
        this_service.deactivate()
        log(service_name + " Deactivated (end)")
    log("Exiting service process loop")
    
    dm_conn_sender.send({"status": "Deactivated"})
    


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-sname",
        "--service_name",
        action="store",
        type=str,
        required=True,
        help="name of the service",
    )
    parser.add_argument(
        "-qsize",
        "--processing_queue_size",
        action="store",
        type=int,
        required=True,
        help="Max size of processing queue",
    )
    parser.add_argument(
        "-fps",
        "--processing_fps",
        action="store",
        type=int,
        required=True,
        help="Max size of processing queue",
    )
    parser.add_argument(
        "-ip",
        "--ip",
        action="store",
        type=str,
        required=True,
        help="IP of device manager listener",
    )
    parser.add_argument(
        "-port",
        "--port",
        action="store",
        type=int,
        required=True,
        help="Port of device manager listener",
    )
    parser.add_argument(
        "-ip_sender",
        "--ip_sender",
        action="store",
        type=str,
        required=True,
        help="IP of device manager sender",
    )
    parser.add_argument(
        "-port_sender",
        "--port_sender",
        action="store",
        type=int,
        required=True,
        help="Port of device manager sender",
    )
    parser.add_argument(
        "-key",
        "--authkey",
        action="store",
        type=str,
        required=True,
        help="Auth key of device manager listener",
    )
    args = parser.parse_args()
    with redirect_stdout(CorticLogger(real_stdout, log_callback)), redirect_stderr(
        CorticLogger(real_stderr, log_callback)
    ):
        main(
            args.service_name,
            args.processing_queue_size,
            args.processing_fps,
            args.ip,
            args.port,
            args.ip_sender,
            args.port_sender,
            args.authkey,
        )
