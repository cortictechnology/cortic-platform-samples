# Service is implemented based on this sample code:
# https://github.com/googlesamples/mediapipe/blob/main/examples/face_detector/python/face_detector.ipynb

from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import os
import math
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red

def _normalized_to_pixel_coordinates(normalized_x, normalized_y, image_width, image_height):
    """Converts normalized value pair to pixel coordinates."""
    
    # Checks if the float value is between 0 and 1.
    def is_valid_normalized_value(value: float) -> bool:
        return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                        math.isclose(1, value))

    if not (is_valid_normalized_value(normalized_x) and
            is_valid_normalized_value(normalized_y)):
        return None
    x_px = min(math.floor(normalized_x * image_width), image_width - 1)
    y_px = min(math.floor(normalized_y * image_height), image_height - 1)
    return x_px, y_px

def process_result(image,detection_result, draw_faces=True):
    """Draws bounding boxes and keypoints on the input image and return it.
    Args:
        image: The input RGB image.
        detection_result: The list of all "Detection" entities to be visualize.
        draw_faces: Whether to draw bounding boxes and keypoints on the input image.
    Returns:
        annotated_image: The image with bounding boxes and keypoints drawn on it.
        detected_faces: The list of detected faces.
        detected_face_keypoints: The list of detected face keypoints.
    """
    annotated_image = image.copy()
    height, width, _ = image.shape
    detected_faces = []
    detected_face_keypoints = []

    for detection in detection_result.detections:
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        detected_faces.append([bbox.origin_x, bbox.origin_y, bbox.origin_x + bbox.width, bbox.origin_y + bbox.height])
        if draw_faces:
            cv2.rectangle(annotated_image, start_point, end_point, TEXT_COLOR, 3)

        for keypoint in detection.keypoints:
            keypoint_px = _normalized_to_pixel_coordinates(keypoint.x, keypoint.y,
                                                        width, height)
            detected_face_keypoints.append([keypoint_px[0], keypoint_px[1]])
            color, thickness, radius = (0, 255, 0), 2, 2
            if draw_faces:
                cv2.circle(annotated_image, keypoint_px, thickness, color, radius)
    
        if draw_faces:
            category = detection.categories[0]
            category_name = category.category_name
            category_name = '' if category_name is None else category_name
            probability = round(category.score, 2)
            result_text = category_name + ' (' + str(probability) + ')'
            text_location = (MARGIN + bbox.origin_x,
                            MARGIN + ROW_SIZE + bbox.origin_y)
            cv2.putText(annotated_image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                        FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    return annotated_image, np.array(detected_faces), np.array(detected_face_keypoints)

class FaceDetection(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}, 
                           "draw_faces": ServiceDataTypes.Boolean}
        self.output_type = {"detected_faces": ServiceDataTypes.NumpyArray, 
                            "detected_face_keypoints": ServiceDataTypes.NumpyArray, 
                            "annotated_image": ServiceDataTypes.CvFrame}
        base_options = python.BaseOptions(model_asset_path=os.path.dirname(os.path.realpath(__file__)) + "/assets/face_detector.tflite")
        self.options = vision.FaceDetectorOptions(base_options=base_options)
        self.detector = None
        
    def activate(self):
        self.detector = vision.FaceDetector.create_from_options(self.options)
        log("FaceDetection: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        numpy_image = input_data["camera_input"]["frame"]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)
        detection_result = self.detector.detect(image)
        annotated_image, detected_faces, detected_face_keypoints = process_result(numpy_image, detection_result, input_data["draw_faces"])
        return {"detected_faces": detected_faces, 
                "detected_face_keypoints": detected_face_keypoints,
                "annotated_image": annotated_image}

    def deactivate(self):
        self.detector = None
        log("FaceDetection: <p style='color:blue'>Deactivated</p>")
