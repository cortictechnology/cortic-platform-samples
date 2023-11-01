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
from labels import idx_list, label_list

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


def process_result(image, detection_result):
    """Draws bounding boxes on the input image and return it.
    Args:
      image: The input RGB image.
      detection_result: The list of all "Detection" entities to be visualize.
    Returns:
      Image with bounding boxes.
    """
    # annotated_image = image.copy()
    image_width = image.shape[1]
    image_height = image.shape[0]
    detected_objects = []

    for detection in detection_result.detections:
        bbox = detection.bounding_box
        x1 = float(bbox.origin_x / image_width)
        y1 = float(bbox.origin_y / image_height)
        x2 = float((bbox.origin_x + bbox.width) / image_width)
        y2 = float((bbox.origin_y + bbox.height) / image_height)

        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if x2 > 1:
            x2 = 1
        if y2 > 1:
            y2 = 1
        # start_point = bbox.origin_x, bbox.origin_y
        # end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        # if draw_detection:
        #     cv2.rectangle(annotated_image, start_point,
        #                   end_point, TEXT_COLOR, 3)

        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)

        position = label_list.index(category_name)
        category_idx = idx_list[position]

        detected_objects.append(
            {'category': category_name,
             'category_id': category_idx,
             'probability': probability,
             'bbox': [x1, y1, x2, y2]})

        # if draw_detection:
        #     result_text = category_name + ' (' + str(probability) + ')'
        #     text_location = (MARGIN + bbox.origin_x,
        #                      MARGIN + ROW_SIZE + bbox.origin_y)
        #     cv2.putText(annotated_image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
        #                 FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    return detected_objects


class ObjectDetection(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}}
        self.output_type = {
            "detections": ServiceDataTypes.List, "frame": ServiceDataTypes.CvFrame}
        self.threshold = 0.5
        base_options = python.BaseOptions(model_asset_path=os.path.dirname(
            os.path.realpath(__file__)) + "/assets/ssd_mobilenet_v2.tflite")
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
        detected_objects = process_result(
            numpy_image, detection_result)
        return {"detections": detected_objects, "frame": numpy_image}

    def deactivate(self):
        self.detector = None
        log("ObjectDetection: <p style='color:blue'>Deactivated</p>")
