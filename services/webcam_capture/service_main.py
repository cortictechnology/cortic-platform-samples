import time
import numpy as np
import cv2
import threading
from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.log_to("webcam_debug.log")
# debugpy.listen(("0.0.0.0", 5678))


class WebcamCaptureService(Service):
    def __init__(self):
        super().__init__()
        self.frame_capturer = None
        self.frame_width = 1280
        self.frame_height = 720
        self.camera_idx = -1
        self.output_type = {"frame": ServiceDataTypes.CvFrame}
        self.stop = False
        self.context.create_state("camera_index", 0)
        self.frame = np.zeros(
            (self.frame_height, self.frame_width, 3), np.uint8)
        self.grab_frame_thread = None

    def activate(self):
        camera_idx_state = self.context.get_state("camera_index")
        if camera_idx_state is not None:
            self.camera_idx = camera_idx_state["camera_index"]
            if self.camera_idx >= 0:
                self.frame_capturer = cv2.VideoCapture(self.camera_idx)
                self.frame_capturer.set(
                    cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.frame_capturer.set(
                    cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                self.stop = False
                self.grab_frame_thread = threading.Thread(
                    target=self.grab_frame_func, daemon=True)
                self.grab_frame_thread.start()
                log("WebcamCapture: <p style='color:blue'>Activated</p>")

    def grab_frame_func(self):
        while not self.stop:
            camera_idx_state = self.context.get_state("camera_index")
            camera_idx = camera_idx_state["camera_index"]
            if camera_idx != self.camera_idx:
                self.camera_idx = camera_idx
                self.frame_capturer.release()
                self.frame_capturer = cv2.VideoCapture(self.camera_idx)
                self.frame_capturer.set(
                    cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.frame_capturer.set(
                    cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            if self.camera_idx >= 0:
                _, frame = self.frame_capturer.read()
                if frame is None:
                    self.frame = np.zeros(
                        (self.frame_height, self.frame_width, 3), np.uint8)
                else:
                    self.frame = frame
            else:
                time.sleep(0.05)

    def process(self, input_data=None):
        if self.frame_capturer is None:
            self.activate()
        if self.frame is None:
            frame = np.zeros(
                (self.frame_height, self.frame_width, 3), np.uint8)
        else:
            frame = self.frame.copy()
        return {"frame": frame}

    def deactivate(self):
        self.stop = True
        if self.grab_frame_thread is not None:
            self.grab_frame_thread.join()
            self.frame_capturer.release()
            self.frame_capturer = None
        log("WebcamCapture: Deactivated")
