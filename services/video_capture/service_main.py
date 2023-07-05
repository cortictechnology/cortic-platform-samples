from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import time
import numpy as np
import cv2

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class VideoCapture(Service):
    def __init__(self):
        super().__init__()
        self.frame_capturer = None
        self.frame_counter = 0
        self.input_type = {"grey_scale": ServiceDataTypes.Boolean}
        self.output_type = {"frame": ServiceDataTypes.CvFrame}

    def activate(self):
        self.video_file = self.context.get_state("video_file", "")
        if self.video_file == "":
            log("No video file specified", LogLevel.Error)
            return
        self.frame_capturer = cv2.VideoCapture(self.video_file)
        log("VideoCapture: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        frame =np.zeros((480, 640, 3), np.uint8)
        if self.video_file == "":
            log("No video file specified", LogLevel.Warning)
            return {"frame": frame}
        _, frame = self.frame_capturer.read()
        if frame is None:
            frame = np.zeros((self.frame_capturer.get(cv2.CAP_PROP_FRAME_HEIGHT), self.frame_capturer.get(cv2.CAP_PROP_FRAME_WIDTH), 3), np.uint8)
        else:
            self.frame_counter += 1
            if self.frame_counter == self.frame_capturer.get(cv2.CAP_PROP_FRAME_COUNT):
                self.frame_counter = 0
                self.frame_capturer.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if input_data["grey_scale"]:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return {"frame": frame}
        
    def deactivate(self):
        self.frame_capturer.release()
        self.frame_capturer = None
        log("VideoCapture: Deactivated")
