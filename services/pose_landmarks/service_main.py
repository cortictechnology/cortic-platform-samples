# Service is implemented based on this sample code:
# https://github.com/googlesamples/mediapipe/blob/main/examples/pose_landmarker/python/%5BMediaPipe_Python_Tasks%5D_Pose_Landmarker.ipynb

from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import os
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

_PRESENCE_THRESHOLD = 0.5
_VISIBILITY_THRESHOLD = 0.5


def process_result(rgb_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    all_pose_landmarks = []

    # Loop through the detected poses to visualize.
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
        ])

        landmarks = []
        for idx, landmark in enumerate(pose_landmarks_proto.landmark):
            if ((landmark.HasField('visibility') and
                landmark.visibility < _VISIBILITY_THRESHOLD) or
                (landmark.HasField('presence') and
                    landmark.presence < _PRESENCE_THRESHOLD)):
                continue
            landmarks.append(
                [landmark.x, landmark.y, landmark.z])
        all_pose_landmarks.append(landmarks)

        # if draw_landmarks:
        #     # Draw the pose landmarks.
        #     solutions.drawing_utils.draw_landmarks(
        #     annotated_image,
        #     pose_landmarks_proto,
        #     solutions.pose.POSE_CONNECTIONS,
        #     solutions.drawing_styles.get_default_pose_landmarks_style())

    return all_pose_landmarks


class PoseLandmarks(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}}
        self.output_type = {"pose_landmarks": ServiceDataTypes.List}

        base_options = python.BaseOptions(model_asset_path=os.path.dirname(
            os.path.realpath(__file__)) + "/assets/pose_landmarker_lite.task")
        self.options = vision.PoseLandmarkerOptions(
            base_options=base_options, output_segmentation_masks=True)
        self.detector = None

    def activate(self):
        self.detector = vision.PoseLandmarker.create_from_options(self.options)
        log("PoseLandmarks: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        numpy_image = input_data["camera_input"]["frame"]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)
        detection_result = self.detector.detect(image)
        pose_landmarks = process_result(
            numpy_image, detection_result)
        return {"pose_landmarks": pose_landmarks}

    def deactivate(self):
        self.detector = None
        log("PoseLandmarks: <p style='color:blue'>Deactivated</p>")
