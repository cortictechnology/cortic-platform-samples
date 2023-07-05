from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import numpy as np
from face_landmarks_detection import FaceLandmarkDetection
from head import PnPHeadPoseEstimator

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class HeadPoseEstimation(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input":{"frame": ServiceDataTypes.CvFrame,
                                           "camera_matrix": ServiceDataTypes.NumpyArray,
                                           "frame_width": ServiceDataTypes.Int,
                                           "frame_height": ServiceDataTypes.Int}}
        self.output_type = {"frame": ServiceDataTypes.CvFrame,
                            "face_location": ServiceDataTypes.List,
                            "face_landmarks": ServiceDataTypes.List,
                            "rvec": ServiceDataTypes.List,
                            "tvec": ServiceDataTypes.List}
        self.camera_parameters = None
        self.frame_width = None
        self.frame_height = None

    def activate(self):
        self.face_landmark_estimator = FaceLandmarkDetection()
        self.head_pose_estimator = PnPHeadPoseEstimator()
        log("HeadPoseEstimation: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        frame = input_data["camera_input"]["frame"]
        if frame.size == 0:
            return {
                "frame": frame,
                "face_location": [],
                "face_landmarks": [],
                "rvec": [],
                "tvec": []
            }
        self.camera_matrix = np.array(input_data["camera_input"]["camera_matrix"])
        fx, _, cx, _, fy, cy, _, _, _ = self.camera_matrix.flatten()
        self.camera_parameters = np.asarray([fx, fy, cx, cy])
        self.frame_width = input_data["camera_input"]["frame_width"]
        self.frame_height = input_data["camera_input"]["frame_height"]
        
        detected_faces, landmarks = self.face_landmark_estimator.detect_landmarks(
            frame, convert_rgb=True
        )
        if detected_faces is not None and landmarks is not None:
            if len(detected_faces) > 0:
                scaled_landmarks = landmarks.copy()
                scaled_landmarks[:, 0] *= frame.shape[1]
                scaled_landmarks[:, 1] *= frame.shape[0]
                face_location = detected_faces[0].copy()
                face_location[0] = face_location[0] / frame.shape[1]
                face_location[1] = face_location[1] / frame.shape[0]
                face_location[2] = face_location[2] / frame.shape[1]
                face_location[3] = face_location[3] / frame.shape[0]
                rvec, tvec = self.head_pose_estimator.fit_func(
                    scaled_landmarks, self.camera_parameters
                )
                frame = self.head_pose_estimator.drawPose(
                    frame, rvec, tvec, self.camera_matrix, np.zeros((1, 4))
                )                            
                return {
                    "frame": frame,
                    "face_location": face_location.tolist(),
                    "face_landmarks": landmarks.tolist(),
                    "rvec": rvec.tolist(),
                    "tvec": tvec.tolist(),
                }
        return {
            "frame": frame,
            "face_location": [],
            "face_landmarks": [],
            "rvec": [],
            "tvec": []
        }

    def deactivate(self):
        self.face_landmark_estimator = None
        self.head_pose_estimator = None
        log("HeadPoseEstimation: <p style='color:blue'>Deactivated</p>")
