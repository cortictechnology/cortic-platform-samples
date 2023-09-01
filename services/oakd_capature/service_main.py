from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import numpy as np
import cv2
from video_capture import VideoCapture

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class OAKDCapture(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"reset_video": ServiceDataTypes.Boolean,
                           "video_file_name": ServiceDataTypes.String}
        self.output_type = {"frame": ServiceDataTypes.CvFrame,
                            "frame_width": ServiceDataTypes.Int,
                            "frame_height": ServiceDataTypes.Int,
                            "camera_matrix": ServiceDataTypes.NumpyArray,
                            "camera_distortion": ServiceDataTypes.NumpyArray,
                            "landmarks_3d": ServiceDataTypes.NumpyArray,
                            }
        self.frame_capturer = None
        self.frame_width = 1280
        self.frame_height = 720
        self.context.create_state("save_path", None)
        self.context.create_state("action", "capture")
        self.context.create_state("open_new_video", "")
        self.context.create_state("landmarks", None)

    def activate(self):
        self.frame_capturer = VideoCapture()
        log("OAKDCapture: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        video_file_name = input_data["video_file_name"]
        if video_file_name == "":
            video_file_name = None
        save_path = None
        save_path_state = self.context.get_state("save_path")
        if save_path_state is not None:
            save_path = save_path_state["save_path"]
        landmarks_3d = np.array([])
        frame = np.zeros((self.frame_height, self.frame_width, 3), np.uint8)

        if input_data["reset_video"]:
            self.frame_capturer.reset_video()
            self.context.reset_states()

        action = "capture"
        action_state = self.context.get_state("action")
        if action_state is not None:
            action = action_state["action"]
        if action == "switch_to_depth":
            self.frame_capturer.switch_to_depth_pipeline()
        elif action == "switch_to_rgb":
            self.frame_capturer.switch_to_rgb_pipeline()
        elif action == "open_new_video":
            video_path = ""
            video_path_state = self.context.get_state("open_new_video")
            if video_path_state is not None:
                video_path = video_path_state["open_new_video"]
            self.frame_capturer.open_new_video(video_path)
        elif action == "depth":
            landmarks = None
            landmarks_state = self.context.get_state("landmarks")
            if landmarks_state is not None:
                landmarks = landmarks_state["landmarks"]
            if landmarks is not None:
                landmarks = np.array(landmarks)
                rois = np.zeros((len(landmarks), 4))
                rois[:, 0] = landmarks[:, 0] - 0.01
                rois[:, 0] = 1 - rois[:, 0]
                rois[:, 1] = landmarks[:, 1] - 0.01
                rois[:, 2] = landmarks[:, 0] + 0.01
                rois[:, 2] = 1 - rois[:, 2]
                rois[:, 3] = landmarks[:, 1] + 0.01
                depth_data = self.frame_capturer.get_depth(rois)
                landmarks_3d = np.array([
                    [
                        d.spatialCoordinates.x,
                        d.spatialCoordinates.y,
                        d.spatialCoordinates.z,
                    ]
                    for d in depth_data
                ])
        elif action == "capture":
            frame = self.frame_capturer.get_frame(
                video_file_name=video_file_name, save_path=save_path
            )
            if frame is None:
                frame = np.zeros(
                    (self.frame_height, self.frame_width, 3), np.uint8)
            frame = cv2.flip(frame, 1)

        return {"frame": frame,
                "frame_width": self.frame_width,
                "frame_height": self.frame_height,
                "camera_matrix": self.frame_capturer.camera_matrix,
                "camera_distortion": self.frame_capturer.camera_distortion,
                "landmarks_3d": landmarks_3d,
                }

    def deactivate(self):
        self.frame_capturer.deactivate()
        self.frame_capturer = None
        log("OAKDCapture: <p style='color:blue'>Deactivated</p>")
