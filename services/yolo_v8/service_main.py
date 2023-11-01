from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
from ultralytics import YOLO
import os
import torch


# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class YoloV8(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"frame_input": {"frame": ServiceDataTypes.CvFrame}, 
                           "threshold": ServiceDataTypes.Float}
        self.output_type = {"detections": ServiceDataTypes.List,
                            "frame": ServiceDataTypes.CvFrame}
        self.model = None
        self.device = "cpu"
        self.loaded_model_name = "yolov8n"
        self.available_models = ["yolov8n", "yolov8s", "yolov8m"]
        self.context.create_state("model", "yolov8n")

    def activate(self):
        model_name = self.context.get_state("model")["model"]
        if model_name not in self.available_models:
            log("Invalid model name. Using default model: yolov8n", LogLevel.Warning)
            model_name = "yolov8n"
        model_path = os.path.dirname(os.path.realpath(__file__)) + "/assets/" + model_name + ".pt"
        self.model = YOLO(model_path)
        if torch.cuda.is_available():
            self.model.to("cuda")
            self.device = "cuda"
        else:
            self.model.to("cpu")
            self.device = "cpu"
        self.loaded_model_name = model_name

    def process(self, input_data=None):
        all_detections = []
        model_name = self.context.get_state("model")["model"]
        if model_name != self.loaded_model_name:
            self.activate()
        names = self.model.names
        frame = input_data["frame_input"]["frame"]
        threshold = input_data["threshold"]
        if frame is None:
            return {"detections": [], "frame": frame}
        results = self.model.predict(source=frame, device=self.device, conf=threshold, verbose=False)
        detections = results[0].boxes.cpu().numpy()
        boxes = detections.xyxyn.tolist()
        confs = detections.conf.tolist()
        clss = detections.cls.tolist()
        classes = []
        for c in clss:
            classes.append(names[int(c)])
        for i in range(len(boxes)):
            result = {"bbox": boxes[i], "probability": confs[i], "category": classes[i], "category_id": clss[i]}
            all_detections.append(result)
        
        return {"detections": all_detections, "frame": frame}

    def deactivate(self):
        self.model = None
