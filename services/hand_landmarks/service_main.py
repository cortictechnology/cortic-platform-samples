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

_PRESENCE_THRESHOLD = 0.5
_VISIBILITY_THRESHOLD = 0.5

def process_result(rgb_image, detection_result, draw_landmarks=True):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)
    all_hand_landmarks = []

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]
        
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])

        landmarks = []
        for idx, landmark in enumerate(hand_landmarks_proto.landmark):
            if ((landmark.HasField('visibility') and
                landmark.visibility < _VISIBILITY_THRESHOLD) or
                (landmark.HasField('presence') and
                    landmark.presence < _PRESENCE_THRESHOLD)):
                continue
            landmarks.append(
                [landmark.x, landmark.y, landmark.z])
        all_hand_landmarks.append(landmarks)

        if draw_landmarks:
            # Draw the hand landmarks.
            solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

            # Get the top left corner of the detected hand's bounding box.
            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks]
            y_coordinates = [landmark.y for landmark in hand_landmarks]
            text_x = int(min(x_coordinates) * width)
            text_y = int(min(y_coordinates) * height) - MARGIN

            # Draw handedness (left or right hand) on the image.
            cv2.putText(annotated_image, f"{handedness[0].category_name}",
                        (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                        FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image, np.array(all_hand_landmarks)

class HandLandmarks(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame},
                           "draw_landmarks": ServiceDataTypes.Boolean}
        self.output_type = {"hand_landmarks": ServiceDataTypes.NumpyArray,
                            "annotated_image": ServiceDataTypes.CvFrame}
        self.num_hands = 2
        base_options = python.BaseOptions(model_asset_path=os.path.dirname(os.path.realpath(__file__)) + "/assets/hand_landmarker.task")
        self.options = vision.HandLandmarkerOptions(base_options=base_options,num_hands=self.num_hands)
        self.detector = None

    def activate(self):
        self.detector = vision.HandLandmarker.create_from_options(self.options)
        log("HandLandmarks: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        numpy_image = input_data["camera_input"]["frame"]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)
        detection_result = self.detector.detect(image)
        annotated_image, hand_landmarks = process_result(
            numpy_image, detection_result, draw_landmarks=input_data["draw_landmarks"])
        return {"hand_landmarks": hand_landmarks, "annotated_image": annotated_image}

    def deactivate(self):
        self.detector = None
        log("HandLandmarks: <p style='color:blue'>Deactivated</p>")
