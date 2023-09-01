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
        self.context.create_state("video_file", "")

    def activate(self):
        self.video_file = ""
        video_file_state = self.context.get_state("video_file")
        if video_file_state is not None:
            self.video_file = video_file_state["video_file"]
        if self.video_file == "":
            log("No video file specified", LogLevel.Error)
            return
        self.frame_capturer = cv2.VideoCapture(self.video_file)
        log("VideoCapture: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        self.video_file = ""
        video_file_state = self.context.get_state("video_file")
        if video_file_state is not None:
            self.video_file = video_file_state["video_file"]
        frame =np.zeros((480, 640, 3), np.uint8)
        if self.video_file == "":
            log("No video file specified", LogLevel.Warning)
            if self.frame_capturer is not None:
                self.frame_capturer.release()
                self.frame_capturer = None
            return {"frame": frame}
        else:
            if self.frame_capturer is None:
                self.frame_capturer = cv2.VideoCapture(self.video_file)
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
