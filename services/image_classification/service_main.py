# Service is implemented based on this sample code:
# https://github.com/googlesamples/mediapipe/blob/main/examples/image_classification/python/image_classifier.ipynb

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

DESIRED_HEIGHT = 480
DESIRED_WIDTH = 480

class ImageClassification(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame},
                           "draw_categories": ServiceDataTypes.Boolean}
        self.output_type = {"categories": ServiceDataTypes.List,
                            "annotated_image": ServiceDataTypes.CvFrame}
        self.top_k = 5
        base_options = python.BaseOptions(model_asset_path=os.path.dirname(
            os.path.realpath(__file__)) + "/assets/efficientnet_lite0.tflite")
        self.options = vision.ImageClassifierOptions(
            base_options=base_options, max_results=self.top_k)
        self.classifier = None

    def activate(self):
        self.classifier = vision.ImageClassifier.create_from_options(self.options)
        log("ImageClassification: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process_result(self, image, classification_result, draw_categories=True):
        annotated_image = image.copy()
        top_classifications = []
        for k in range(self.top_k):
            catetory_name = classification_result.classifications[0].categories[k].category_name
            score = classification_result.classifications[0].categories[k].score
            top_classifications.append(
                {"category_name": catetory_name, "score": score})
            if draw_categories:
                text = "{:.1f}".format(score * 100) + "% - " + catetory_name
                cv2.putText(annotated_image, text, (9, 30+30*k-1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                cv2.putText(annotated_image, text, (10, 30+30*k), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

        return annotated_image, top_classifications

    def process(self, input_data=None):
        numpy_image = input_data["camera_input"]["frame"]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)
        classification_result = self.classifier.classify(image)
        annotated_image, top_classifications = self.process_result(
            numpy_image, classification_result, input_data["draw_categories"])
        return {"categories": top_classifications, "annotated_image": annotated_image}

    def deactivate(self):
        self.classifier = None
        log("ImageClassification: <p style='color:blue'>Deactivated</p>")
