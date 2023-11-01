from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
from boxmot import BYTETracker
import numpy as np

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class ByteTracker(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"detection_result": {"detections": ServiceDataTypes.List, 
                                                "frame": ServiceDataTypes.CvFrame}}
        self.output_type = {"detections": ServiceDataTypes.List, "frame": ServiceDataTypes.CvFrame}
        self.tracker = None

    def activate(self):
        self.tracker = BYTETracker()

    def process(self, input_data=None):
        detections = input_data["detection_result"]["detections"]
        frame = input_data["detection_result"]["frame"]
        width, height = frame.shape[1], frame.shape[0]
        all_detections = []
        tracked_detections = []
        category_association = {}
        for detection in detections:
            bbox = detection["bbox"]
            bbox[0] = bbox[0] * width
            bbox[1] = bbox[1] * height
            bbox[2] = bbox[2] * width
            bbox[3] = bbox[3] * height
            probability = detection["probability"]
            category_id = detection["category_id"]
            category_association[category_id] = detection["category"]
            all_detections.append([bbox[0], bbox[1], bbox[2], bbox[3], probability, category_id])
        if len(all_detections) == 0:
            return {"detections": tracked_detections, "frame": frame}
        dets = np.array(all_detections)
        tracks = self.tracker.update(dets, frame)
    
        xyxys = tracks[:, 0:4].astype('int')
        ids = tracks[:, 4].astype('int')
        confs = tracks[:, 5]
        clss = tracks[:, 6].astype('int')
        inds = tracks[:, 7].astype('int')
    
        if tracks.shape[0] != 0:
            for xyxy, id, conf, cls in zip(xyxys, ids, confs, clss):
                tracked_detections.append({
                    "bbox": [xyxy[0] / width, xyxy[1] / height, xyxy[2] / width, xyxy[3] / height],
                    "probability": float(conf),
                    "category": category_association[cls] + ", id: " + str(id),
                    "id": int(id)
                })
        return {"detections": tracked_detections, "frame": frame}

    def deactivate(self):
        self.tracker = None
