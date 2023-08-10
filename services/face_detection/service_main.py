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

def process_result(image,detection_result):
    height, width, _ = image.shape
    detected_faces = []
    detected_face_keypoints = []

    for detection in detection_result.detections:
        bbox = detection.bounding_box
        x1 = float(bbox.origin_x/width)
        y1 = float(bbox.origin_y/height)
        x2 = float((bbox.origin_x + bbox.width)/width)
        y2 = float((bbox.origin_y + bbox.height)/height)
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if x2 > 1:
            x2 = 1
        if y2 > 1:
            y2 = 1
        detected_faces.append([x1, y1, x2, y2])
        
        for keypoint in detection.keypoints:
            # keypoint_px = _normalized_to_pixel_coordinates(keypoint.x, keypoint.y,
                                                        # width, height)
            detected_face_keypoints.append([keypoint.x, keypoint.y])

    return detected_faces, detected_face_keypoints

class FaceDetection(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}}
        self.output_type = {"detected_faces": ServiceDataTypes.List, 
                            "detected_face_keypoints": ServiceDataTypes.List}
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
        detected_faces, detected_face_keypoints = process_result(numpy_image, detection_result)
        return {"detected_faces": detected_faces, 
                "detected_face_keypoints": detected_face_keypoints}

    def deactivate(self):
        self.detector = None
        log("FaceDetection: <p style='color:blue'>Deactivated</p>")
