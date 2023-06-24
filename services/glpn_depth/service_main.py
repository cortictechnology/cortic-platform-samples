from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
import torch
import numpy as np
from PIL import Image

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

class GLPNMonocularDepthEstimation(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"image": ServiceDataTypes.CvFrame}
        self.output_type = {"raw_depth": ServiceDataTypes.NumpyArray, 
                            "depth_image": ServiceDataTypes.CvFrame}
        self.checkpoint = "vinvino02/glpn-nyu"
        self.image_processor = None
        self.model = None

    def activate(self):
        self.image_processor = AutoImageProcessor.from_pretrained(self.checkpoint)
        self.model = AutoModelForDepthEstimation.from_pretrained(self.checkpoint)
        log("GLPNDepthEstimation: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        image = Image.fromarray(input_data["image"].astype('uint8'), 'RGB')
        pixel_values = self.image_processor(image, return_tensors="pt").pixel_values
        with torch.no_grad():
            outputs = self.model(pixel_values)
            predicted_depth = outputs.predicted_depth

        # interpolate to original size
        prediction = torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size=image.size[::-1],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

        # visualize the prediction
        output = prediction.numpy()
        formatted = (output * 255 / np.max(output)).astype("uint8")
        return {"raw_depth": output, "depth_image": formatted}

    def deactivate(self):
        self.image_processor = None
        self.model = None
        log("GLPNDepthEstimation: <p style='color:blue'>Deactivated</p>")
