# Service is implemented based on this sample code:
# https://github.com/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb


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

mp_hands = mp.solutions.hands

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

def process_result(detection_result):
    all_hand_landmarks = []
    all_handedness = []

    if detection_result.multi_hand_landmarks is None:
        return all_hand_landmarks, all_handedness
    
    if detection_result.multi_handedness is None:
        return all_hand_landmarks, all_handedness

    for hand_landmarks in detection_result.multi_hand_landmarks:
        landmarks = []
        for landmark in hand_landmarks.landmark:
            landmarks.append(
                [landmark.x, landmark.y, landmark.z])
        all_hand_landmarks.append(landmarks)

    for handedness in detection_result.multi_handedness:
        all_handedness.append(handedness.classification[0].label)

    return all_hand_landmarks, all_handedness

class HandLandmarks(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}}
        self.output_type = {"frame": ServiceDataTypes.CvFrame,
                            "hand_landmarks": ServiceDataTypes.List, 
                            "handedness": ServiceDataTypes.List}
        self.num_hands = 2
        self.min_detection_confidence = 0.5
        self.min_tracking_confidence = 0.5
        self.detector = None

    def activate(self):
        self.detector = mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
            max_num_hands=self.num_hands)
        log("HandLandmarks: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        numpy_image = input_data["camera_input"]["frame"]
        image = cv2.cvtColor(numpy_image, cv2.COLOR_BGR2RGB)
        detection_result = self.detector.process(image)
        hand_landmarks, handedness = process_result(detection_result)
        return {"frame": numpy_image,
                "hand_landmarks": hand_landmarks,
                "handedness": handedness}

    def deactivate(self):
        self.detector = None
        log("HandLandmarks: <p style='color:blue'>Deactivated</p>")
