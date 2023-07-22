from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import numpy as np
import cv2
from PIL import Image
from facemesh_mp import FaceMeshEstimationMp
from iris_detection import IrisDetector
from blink_counter import BlinkCounter

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

EAR_THRESH = 0.05


class IrisDetection(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input":{"frame": ServiceDataTypes.CvFrame,
                                           "camera_matrix": ServiceDataTypes.NumpyArray,
                                           "frame_width": ServiceDataTypes.Int,
                                           "frame_height": ServiceDataTypes.Int}}
        self.output_type = {"frame": ServiceDataTypes.CvFrame,
                            "face_location": ServiceDataTypes.List,
                            "right_iris_location": ServiceDataTypes.List,
                            "left_iris_location": ServiceDataTypes.List,
                            "center_point": ServiceDataTypes.List,
                            "num_blinks": ServiceDataTypes.Int}

    def activate(self):
        self.facemesh_estimator = FaceMeshEstimationMp()
        self.iris_detector = IrisDetector()
        self.blink_count = BlinkCounter(EAR_THRESH)
        log("IrisDetection: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        camera_matrix = np.array(input_data["camera_input"]["camera_matrix"])
        focal_length = (camera_matrix[0, 0] + camera_matrix[1, 1]) / 2
        self.iris_detector.frame_width = input_data["camera_input"]["frame_width"]
        self.iris_detector.frame_height = input_data["camera_input"]["frame_height"]
        self.iris_detector.image_size = (
                self.iris_detector.frame_width,
                self.iris_detector.frame_height,
            )
        self.iris_detector.focal_length = focal_length
        self.blink_count.frame_width = input_data["camera_input"]["frame_width"]
        self.blink_count.frame_height = input_data["camera_input"]["frame_height"]
        
        if self.context.get_state("reset_blink", False):
            self.blink_count.num_blinks = 0
            self.context.set_states({"reset_blink": False})
        
        frame = input_data["camera_input"]["frame"]
        cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.asarray(Image.fromarray(cv2_im_rgb), dtype=np.uint8)
        landmarks, detected_faces = self.facemesh_estimator.get_facemesh(frame_rgb)

        if landmarks is not None and detected_faces is not None:
            num_blinks = self.blink_count.count_blink(landmarks)
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
            right_iris_landmarks[:, 0] = right_iris_landmarks[:, 0] - landmarks[0, 6]
            right_iris_landmarks[:, 1] = right_iris_landmarks[:, 1] - landmarks[1, 6]
            left_iris_landmarks[:, 0] = left_iris_landmarks[:, 0] - landmarks[0, 6]
            left_iris_landmarks[:, 1] = left_iris_landmarks[:, 1] - landmarks[1, 6]
            return {
                    "frame": frame,
                    "face_location": detected_faces[0],
                    "right_iris_location": right_iris_landmarks[0].tolist(),
                    "left_iris_location": left_iris_landmarks[0].tolist(),
                    "center_point": landmarks[:, 6].tolist(),
                    "num_blinks": num_blinks,
                }
        else:
            return {
                    "frame": frame,
                    "face_location": [],
                    "right_iris_location": [],
                    "left_iris_location": [],
                    "center_point": [],
                    "num_blinks": self.blink_count.num_blinks
                }

    def deactivate(self):
        self.facemesh_estimator = None
        self.iris_detector = None
        self.blink_count = None
        log("IrisDetection: <p style='color:blue'>Deactivated</p>")
