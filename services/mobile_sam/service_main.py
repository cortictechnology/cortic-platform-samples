from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import os
import cv2
import torch
import numpy as np
from mobile_encoder.setup_mobile_sam import setup_model
from mobile_sam import SamPredictor

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

MASK_COLOR = np.array([255, 144, 30])

class MobileSAM(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"image": ServiceDataTypes.CvFrame, 
                           "input_points": ServiceDataTypes.NumpyArray,
                           "input_labels": ServiceDataTypes.NumpyArray,
                           "input_box": ServiceDataTypes.NumpyArray,
                           "use_previous_mask": ServiceDataTypes.Boolean}
        self.output_type = {"masks": ServiceDataTypes.NumpyArray, 
                            "scores": ServiceDataTypes.NumpyArray,
                            "masked_image": ServiceDataTypes.CvFrame}
        self.model_path = os.path.dirname(os.path.realpath(__file__)) + "/assets/mobile_sam.pt"

    def activate(self):
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        if torch.backends.mps.is_available():
            device = "mps"
        checkpoint = torch.load(self.model_path, map_location=torch.device(device))
        self.mobile_sam = setup_model()
        self.mobile_sam.load_state_dict(checkpoint,strict=True)
        self.mobile_sam.to(device=device)
        self.mobile_sam.eval()
        self.predictor = SamPredictor(self.mobile_sam)
        log("MobileSAM: <p style='color:blue'>Activated</p>")

    def draw_mask(self, image, mask, points=None, labels=None, box=None):
        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1) * MASK_COLOR.reshape(1, 1, -1)
        mask_image = mask_image.astype(np.uint8)
        masked_image = cv2.addWeighted(image, 0.5, mask_image, 0.5, 0)
        if points is not None and labels is not None:
            i = 0
            for point in points:
                x, y = point
                if labels[i] == 1:
                    cv2.drawMarker(masked_image, (x, y), (0, 255, 0), cv2.MARKER_TILTED_CROSS, int(h*0.035), 2)
                else:
                    cv2.drawMarker(masked_image, (x, y), (0, 0, 255), cv2.MARKER_TILTED_CROSS, int(h*0.035), 2)
                i += 1
        if box is not None:
            x1, y1, x2, y2 = box
            cv2.rectangle(masked_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        return masked_image

    def process(self, input_data=None):
        current_image = self.context.get_state("image", None)
        if current_image is None:
            self.predictor.set_image(input_data["image"])
            self.context.set_states({"image": input_data["image"]})
        if input_data["input_points"].size == 0 and input_data["input_box"].size == 0:
            return {"masks": [], "scores": [], "masked_image": input_data["image"]}
        else:
            if input_data["input_points"].size == 0 and input_data["input_box"].size != 0:
                self.context.reset_states()
                masks, scores, logits = self.predictor.predict(
                    point_coords=None,
                    point_labels=None,
                    box=input_data["input_box"][None, :],
                    multimask_output=False,
                )
                masked_image = self.draw_mask(input_data["image"], masks[0], box=input_data["input_box"])
                self.context.set_states({"mask_input": logits[0, :, :]})
                return {"masks": masks, "scores": scores, "masked_image": masked_image}
            if input_data["input_points"].size != 0:
                if input_data["input_labels"].size == 0:
                    return {"masks": [], "scores": [], "masked_image": input_data["image"]}
                else:
                    points = self.context.get_state("points", None)
                    labels = self.context.get_state("labels", None)
                    mask_input = None
                    if input_data["use_previous_mask"]:
                        mask_input = self.context.get_state("mask_input", None)
                        if mask_input is not None:
                            mask_input = mask_input[None, :, :]
                    if points is None:
                        points = input_data["input_points"]
                    else:
                        points = np.concatenate((points, input_data["input_points"]), axis=0)
                    if labels is None:
                        labels = input_data["input_labels"]
                    else:
                        labels = np.concatenate((labels, input_data["input_labels"]), axis=0)
                    masks, scores, logits = self.predictor.predict(
                        point_coords=points,
                        point_labels=labels,
                        mask_input=mask_input,
                        multimask_output=self.context.get_state("multimask_output", True),
                    )
                    
                    masked_image = self.draw_mask(input_data["image"], masks[np.argmax(scores)], points=points, labels=labels)
                    self.context.set_states({"mask_input": logits[np.argmax(scores), :, :]})
                    self.context.set_states({"points": points})
                    self.context.set_states({"labels": labels})
                    return {"masks": masks, "scores": scores, "masked_image": masked_image}

    def deactivate(self):
        self.mobile_sam = None
        self.predictor = None
        log("MobileSAM: <p style='color:blue'>Deactivated</p>")
