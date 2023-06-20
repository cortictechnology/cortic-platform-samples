# Service is implemented based on this sample code:
# https://github.com/googlesamples/mediapipe/blob/main/examples/object_detection/python/object_detector.ipynb

from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import os
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

MARGIN = 20  # pixels
ROW_SIZE = 20  # pixels
FONT_SIZE = 2
FONT_THICKNESS = 2
TEXT_COLOR = (255, 255, 255)  # red


def process_result(image, detection_result, draw_detection=True):
    """Draws bounding boxes on the input image and return it.
    Args:
      image: The input RGB image.
      detection_result: The list of all "Detection" entities to be visualize.
    Returns:
      Image with bounding boxes.
    """
    annotated_image = image.copy()
    detected_objects = []

    for detection in detection_result.detections:
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        if draw_detection:
            cv2.rectangle(annotated_image, start_point,
                          end_point, TEXT_COLOR, 3)

        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)

        detected_objects.append(
            {'category': category_name, 'probability': probability, 'bbox': [bbox.origin_x, bbox.origin_y, bbox.origin_x + bbox.width, bbox.origin_y + bbox.height]})

        if draw_detection:
            result_text = category_name + ' (' + str(probability) + ')'
            text_location = (MARGIN + bbox.origin_x,
                             MARGIN + ROW_SIZE + bbox.origin_y)
            cv2.putText(annotated_image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                        FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    return annotated_image, detected_objects


class ObjectDetection(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame},
                           "draw_objects": ServiceDataTypes.Boolean}
        self.output_type = {"detected_objects": ServiceDataTypes.List,
                            "annotated_image": ServiceDataTypes.CvFrame}
        self.threshold = 0.5
        base_options = python.BaseOptions(model_asset_path=os.path.dirname(
            os.path.realpath(__file__)) + "/assets/efficientdet_lite0.tflite")
        self.options = vision.ObjectDetectorOptions(base_options=base_options,
                                                    score_threshold=self.threshold)
        self.detector = None

    def activate(self):
        self.detector = vision.ObjectDetector.create_from_options(self.options)
        log("ObjectDetection: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        numpy_image = input_data["camera_input"]["frame"]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)
        detection_result = self.detector.detect(image)
        annotated_image, detected_objects = process_result(
            numpy_image, detection_result, input_data["draw_objects"])
        return {"detected_objects": detected_objects,
                "annotated_image": annotated_image}

    def deactivate(self):
        self.detector = None
        log("ObjectDetection: <p style='color:blue'>Deactivated</p>")
