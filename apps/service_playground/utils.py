import json
import ast
import numpy as np


def get_service_input_list(service_data):
    service_input = service_data["input_type"]
    if len(service_input) > 0:
        service_input_list = []
        for key in service_input:
            if isinstance(service_input[key], dict):
                for sub_key in service_input[key]:
                    service_input_list.append(
                        key + "." + sub_key + " (" + service_input[key][sub_key].name + ")")
            else:
                service_input_list.append(
                    key + " (" + service_input[key].name + ")")
        return service_input_list
    else:
        return []


def get_service_output_list(service_data):
    service_output = service_data["output_type"]
    if len(service_output) > 0:
        service_output_list = []
        for key in service_output:
            if isinstance(service_output[key], dict):
                for sub_key in service_output[key]:
                    service_output_list.append(
                        key + "." + sub_key + " (" + service_output[key][sub_key].name + ")")
            else:
                service_output_list.append(
                    key + " (" + service_output[key].name + ")")
        return service_output_list
    else:
        return []


def get_data_type(field_name):
    start_idx = field_name.find("(") + 1
    end_idx = field_name.find(")")
    return field_name[start_idx:end_idx]


def generate_service_input_data(service_data, input_data):
    service_input = service_data["input_type"]
    if len(service_input) > 0:
        service_input_data = {}
        for key in service_input:
            if isinstance(service_input[key], dict):
                service_input_data[key] = {}
                for sub_key in service_input[key]:
                    service_input_data[key][sub_key] = input_data[key + "." + sub_key +
                                                                  " (" + service_input[key][sub_key].name + ")"]
            else:
                service_input_data[key] = input_data[key +
                                                     " (" + service_input[key].name + ")"]
        return service_input_data
    else:
        return {}


def encode_input(data_type, data):
    if data_type == "NumpyArray":
        array_data = data
        if not isinstance(array_data, np.ndarray):
            if isinstance(array_data, str):
                array_data = ast.literal_eval(array_data)
            try:
                array_data = np.array(array_data)
            except:
                raise Exception(
                    "Invalid input data type for NumpyArray, cannot convert to numpy array")
        return array_data
    elif data_type == "Int":
        return int(data)
    elif data_type == "Float":
        return float(data)
    elif data_type == "String":
        return str(data)
    elif data_type == "Json":
        try:
            return ast.literal_eval(data)
        except:
            return None
    elif data_type == "List":
        if data[0] != "[" and data[-1] != "]":
            data = "[" + data + "]"
        return ast.literal_eval(data)
    elif data_type == "Boolean":
        return data
    else:
        return ast.literal_eval(data)


def encode_state_value(data_type, data):
    if data_type == "NumpyArray":
        return np.array(ast.literal_eval(data)).tolist()
    elif data_type == "Int":
        return int(data)
    elif data_type == "Float":
        return float(data)
    elif data_type == "String":
        return str(data)
    elif data_type == "Json":
        if data[0] != "{" and data[-1] != "}":
            data = "{" + data + "}"
        data = ast.literal_eval(data)
        data = json.dumps(data)
        return data
    elif data_type == "List":
        if data[0] != "[" and data[-1] != "]":
            data = "[" + data + "]"
        return ast.literal_eval(data)
    elif data_type == "Boolean":
        if data == "True" or data == "true" or data == "1":
            return True
        else:
            return False
    else:
        return data


def decode_output(data_type, data):
    if data_type == "NumpyArray":
        return data
    elif data_type == "Int":
        return str(int(data))
    elif data_type == "Float":
        return str(float(data))
    elif data_type == "String":
        return str(data)
    elif data_type == "Json":
        return json.dumps(data)
    elif data_type == "List":
        return data
    else:
        return data
