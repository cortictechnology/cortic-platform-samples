import os
import platform
from cortic_platform.sdk.service import Service
from cortic_platform.sdk.service_data_types import ServiceDataTypes

if platform.system() == "Darwin":
    from face_detector import FaceDetector
else:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class FaceDetectorMultiplaform(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}}
        self.output_type = {"detected_faces": ServiceDataTypes.List}

        if platform.system() != "Darwin":
            # Linux or Windows
            model_path = os.path.dirname(os.path.realpath(__file__)) + "/assets/face_detector.tflite"
            base_options = python.BaseOptions(model_asset_path=model_path)
            self.options = vision.FaceDetectorOptions(base_options=base_options)

        self.detector = None

    def activate(self):
        if platform.system() == "Darwin":
            self.detector = FaceDetector()
        else:
            self.detector = vision.FaceDetector.create_from_options(self.options)

    def process(self, input_data=None):
        frame = input_data["camera_input"]["frame"]
        if platform.system() == "Darwin":
            detection_result = self.detector.run_inference(frame)
        else:
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            detection_result = self.detector.detect(image)

        detected_faces = self._process_result(frame, detection_result)
        return {"detected_faces": detected_faces}
    
    def _process_result(self, frame, detection_result):
        height, width, _ = frame.shape
        detected_faces = []

        if platform.system() == "Darwin":
            for face in detection_result:
                face_coordinates = face["face_coordinates"]
                x1 = face_coordinates[0]
                y1 = face_coordinates[1]
                x2 = face_coordinates[2]
                y2 = face_coordinates[3]
                detected_faces.append([x1, y1, x2, y2])
        else:
            for detection in detection_result.detections:
                bbox = detection.bounding_box
                x1 = float(bbox.origin_x/width)
                y1 = float(bbox.origin_y/height)
                x2 = float((bbox.origin_x + bbox.width)/width)
                y2 = float((bbox.origin_y + bbox.height)/height)
                detected_faces.append([x1, y1, x2, y2])
        return detected_faces

    def deactivate(self):
        self.detector = None
