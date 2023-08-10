import os
import torch
import cv2
from blazeface import BlazeFace # This is the file from the BlazeFace project by hollance
from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class FaceDetectionPytorch(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}}
        self.output_type = {"detected_faces": ServiceDataTypes.List}
        
        # This is where the service decides which backend to use
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda:0"
        elif torch.backends.mps.is_available():
            device = "mps"
        self.device = torch.device(device)

        self.detector = None

    def activate(self):
        self.detector = BlazeFace().to(self.device)
        self.detector.load_weights(os.path.dirname(os.path.realpath(__file__)) + "/assets/blazeface.pth")
        self.detector.load_anchors(os.path.dirname(os.path.realpath(__file__)) + "/assets/anchors.npy")
        self.detector.min_score_thresh = 0.75

    def process(self, input_data=None):
        numpy_image = input_data["camera_input"]["frame"]
        img = cv2.cvtColor(numpy_image, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (128, 128))
        detection_result = self.detector.predict_on_image(img).detach().cpu().numpy()
        detected_faces = self._process_result(detection_result)
        return {"detected_faces": detected_faces}
    
    def _process_result(self, detection_result):
        detected_faces = []

        for i in range(detection_result.shape[0]):
            y1 = detection_result[i, 0].item()
            x1 = detection_result[i, 1].item()
            y2 = detection_result[i, 2].item()
            x2 = detection_result[i, 3].item()
            detected_faces.append([x1, y1, x2, y2])

        return detected_faces

    def deactivate(self):
        self.detector = None