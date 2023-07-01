from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import cv2
import numpy as np
from supported_functions import supported_functions

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class OpenCVImageProcessing(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"image_input": {"frame": ServiceDataTypes.CvFrame}, 
                           "mode": ServiceDataTypes.String,
                           "parameters": ServiceDataTypes.List}
        self.output_type = {"processed_image": ServiceDataTypes.CvFrame}

    def activate(self):
        log("OpenCVImageProcessing: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        if input_data["mode"] not in supported_functions:
            return {"processed_image": input_data["image"]}
        processing_function = getattr(cv2, input_data["mode"])
        parameters = input_data["parameters"]
        if input_data["mode"] == "dilate" or input_data["mode"] == "erode" or input_data["mode"] == "filter2D":
            for i in range(len(parameters)):
                if isinstance(parameters[i], list):
                    parameters[i] = np.array(parameters[i])
        processed_image = processing_function(input_data["image_input"]["frame"], *parameters)
        return {"processed_image": processed_image}

    def deactivate(self):
        log("OpenCVImageProcessing: <p style='color:blue'>Deactivated</p>")
