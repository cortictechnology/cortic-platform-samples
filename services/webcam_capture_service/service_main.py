import time
import numpy as np
import cv2
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
        self.input_type = {"grey_scale": ServiceDataTypes.Boolean}
        self.output_type = {"frame": ServiceDataTypes.CvFrame}

    def activate(self):
        self.frame_capturer = cv2.VideoCapture(0)
        self.frame_capturer.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.frame_capturer.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        log("WebcamCapture: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        frame = None
        _, frame = self.frame_capturer.read()
        if frame is None:
            frame = np.zeros((self.frame_height, self.frame_width, 3), np.uint8)
        if input_data["grey_scale"]:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return {"frame": frame}

    def deactivate(self):
        self.frame_capturer.release()
        self.frame_capturer = None
        log("WebcamCapture: Deactivated")
