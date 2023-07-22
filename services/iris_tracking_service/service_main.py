import time
import numpy as np
import cv2
from PIL import Image
from facemesh_mp import FaceMeshEstimationMp
from iris_detection import IrisDetection
from blink_counter import BlinkCounter
from head_geometry import HeadPoseEstimation
import base64
from cortic_aiot.sdk.service import Service
from cortic_aiot.sdk.logging import log, LogLevel
from cortic_aiot.sdk.service_data_types import ServiceDataTypes

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

EAR_THRESH = 0.05


class IrisTrackingService(Service):
    def __init__(self):
        super().__init__()
        self.get_head_pose = False
        self.type = "iris_tracking"
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}}
        self.output_type = {
            "frame": ServiceDataTypes.CvFrame,
            "rvec": ServiceDataTypes.NumpyArray,
            "tvec": ServiceDataTypes.NumpyArray,
            "face_location": ServiceDataTypes.NumpyArray,
            "right_iris_location": ServiceDataTypes.NumpyArray,
            "left_iris_location": ServiceDataTypes.NumpyArray,
            "center_point": ServiceDataTypes.NumpyArray,
            "num_blinks": ServiceDataTypes.Int,
        }

    def activate(self):
        self.facemesh_estimator = FaceMeshEstimationMp()
        self.iris_detector = IrisDetection()
        self.iris_detector.frame_width = 1280
        self.iris_detector.frame_height = 720
        self.iris_detector.image_size = (
            self.iris_detector.frame_width,
            self.iris_detector.frame_height,
        )
        self.iris_detector.focal_length = 600
        self.blink_count = BlinkCounter(EAR_THRESH)
        self.blink_count.frame_width = 1280
        self.blink_count.frame_height = 720
        self.head_pose_estimator = HeadPoseEstimation()
        print("IrisTracking: Activated")

    def process(self, input_data=None):
        # if (
        #     "action" in input_data["data"][0]
        #     and input_data["data"][0]["action"] == "config"
        # ):
        #     self.iris_detector.frame_width = input_data["data"][0]["frame_width"]
        #     self.iris_detector.frame_height = input_data["data"][0]["frame_height"]
        #     self.iris_detector.image_size = (
        #         self.iris_detector.frame_width,
        #         self.iris_detector.frame_height,
        #     )
        #     self.iris_detector.focal_length = input_data["data"][0]["focal_length"]
        #     self.blink_count.frame_width = input_data["data"][0]["frame_width"]
        #     self.blink_count.frame_height = input_data["data"][0]["frame_height"]
        #     self.camera_matrix = np.array(input_data["data"][0]["camera_matrix"])
        #     self.blink_count.num_blinks = 0
        #     print("Iris Tracking service config finished")
        #     return True

        # if "reset_blink" in input_data["data"][0]:
        #     self.blink_count.num_blinks = 0
        #     print("Reset blink counter")
        #     return True

        # if "calibration_mode" in input_data["data"][0]:
        #     self.get_head_pose = True
        #     return True

        # if "okn_mode" in input_data["data"][0]:
        #     self.get_head_pose = False
        #     return True

        frame = input_data["camera_input"]["frame"]
        cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.asarray(Image.fromarray(cv2_im_rgb), dtype=np.uint8)
        landmarks, detected_faces = self.facemesh_estimator.get_facemesh(frame_rgb)
        rvec = np.array([])
        tvec = np.array([])
        if landmarks is not None:
            num_blinks = self.blink_count.count_blink(landmarks)
            try:
                (
                    right_iris_landmarks,
                    left_iris_landmarks,
                    left_depth,
                    right_depth,
                ) = self.iris_detector.get_iris(frame_rgb, landmarks)
                frame = self.iris_detector.draw_iris(
                    frame,
                    right_iris_landmarks,
                    left_iris_landmarks,
                    left_depth,
                    right_depth,
                )
                right_iris_landmarks[:, 0] = (
                    right_iris_landmarks[:, 0] - landmarks[0, 6]
                )
                right_iris_landmarks[:, 1] = (
                    right_iris_landmarks[:, 1] - landmarks[1, 6]
                )
                left_iris_landmarks[:, 0] = left_iris_landmarks[:, 0] - landmarks[0, 6]
                left_iris_landmarks[:, 1] = left_iris_landmarks[:, 1] - landmarks[1, 6]
            except:
                return {
                    "frame": frame,
                    "rvec": rvec,
                    "tvec": tvec,
                    "face_location": None,
                    "right_iris_location": [],
                    "left_iris_location": [],
                    "center_point": [],
                    "num_blinks": 0,
                }
            if self.get_head_pose:
                (
                    _,
                    _,
                    _,
                    model_points,
                    rvec,
                    tvec,
                ) = self.head_pose_estimator.get_head_pose(
                    landmarks,
                    self.iris_detector.frame_width,
                    self.iris_detector.frame_height,
                    self.camera_matrix,
                )

                frame = self.head_pose_estimator.draw_head_pose(
                    frame, model_points, rvec, tvec, self.camera_matrix
                )
                return {
                    "frame": frame,
                    "rvec": rvec,
                    "tvec": tvec,
                    "face_location": np.array(detected_faces[0]),
                    "right_iris_location": right_iris_landmarks[0],
                    "left_iris_location": left_iris_landmarks[0],
                    "center_point": landmarks[:, 6],
                    "num_blinks": num_blinks,
                }
            else:
                return {
                    "frame": frame,
                    "rvec": rvec,
                    "tvec": tvec,
                    "face_location": np.array(detected_faces[0]),
                    "right_iris_location": right_iris_landmarks[0],
                    "left_iris_location": left_iris_landmarks[0],
                    "center_point": landmarks[:, 6],
                    "num_blinks": num_blinks,
                }
        else:
            return {
                "frame": frame,
                "rvec": rvec,
                "tvec": tvec,
                "face_location": np.array([]),
                "right_iris_location": np.array([]),
                "left_iris_location": np.array([]),
                "center_point": np.array([]),
                "num_blinks": 0,
            }

    def deactivate(self):
        print("IrisTracking: Deactivated")
