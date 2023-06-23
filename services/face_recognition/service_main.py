from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import os
import os.path as osp
import cv2
import numpy as np
import onnxruntime
from scrfd import SCRFD
from arcface_onnx import ArcFaceONNX

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class FaceRecognition(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"reference_image": ServiceDataTypes.CvFrame, "query_image": ServiceDataTypes.CvFrame}
        self.output_type = {"similarity": ServiceDataTypes.Float, "message": ServiceDataTypes.String}
        self.assets_dir = osp.expanduser(os.path.dirname(os.path.realpath(__file__)) + '/assets/buffalo_l')
        self.detector = None
        self.recognizer = None

    def activate(self):
        self.detector = SCRFD(os.path.join(self.assets_dir, 'det_10g.onnx'))
        self.recognizer = ArcFaceONNX(os.path.join(self.assets_dir, 'w600k_r50.onnx'))
        # Change to 0 or higher to use GPU
        self.detector.prepare(-1)
        # Change to 0 or higher to use GPU
        self.recognizer.prepare(-1)
        log("FaceRecognition: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        bboxes1, kpss1 = self.detector.autodetect(input_data["reference_image"], max_num=1)
        if bboxes1.shape[0]==0:
            return {"similarity": -1.0, "message": "Face not found in Reference Image"}
        bboxes2, kpss2 = self.detector.autodetect(input_data["query_image"], max_num=1)
        if bboxes2.shape[0]==0:
            return {"similarity": -1.0, "message": "Face not found in Query Image"}
        kps1 = kpss1[0]
        kps2 = kpss2[0]
        feat1 = self.recognizer.get(input_data["reference_image"], kps1)
        feat2 = self.recognizer.get(input_data["query_image"], kps2)
        sim = self.recognizer.compute_sim(feat1, feat2)
        return {"similarity": sim, "message": "Comparison Successful"}

    def deactivate(self):
        self.detector = None
        self.recognizer = None
        log("FaceRecognition: <p style='color:blue'>Deactivated</p>")
