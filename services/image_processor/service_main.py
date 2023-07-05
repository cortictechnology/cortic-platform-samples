from cortic_aiot.sdk.service import Service
from cortic_aiot.sdk.logging import log, LogLevel
import cv2
import base64
import numpy as np
from cortic_aiot.sdk.service_data_types import ServiceDataTypes

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class ImageProcessingService(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {
            "image": ServiceDataTypes.CvFrame,
            "mode": ServiceDataTypes.String,
        }
        self.output_type = {"processed_image": ServiceDataTypes.CvFrame}
        self.image_processing_functions = {
            "cartoonify": self.cartoonify_image,
            "edge_detection": self.edge_detection,
            "contour_detection": self.contour_detection,
        }

    def activate(self):
        log("ImageProcessingService: Activated")

    def configure(self, params):
        pass

    def edge_mask(self, img, line_size, blur_value):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, blur_value)
        edges = cv2.adaptiveThreshold(
            gray_blur,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            line_size,
            blur_value,
        )
        return edges

    def color_quantization(self, img, k):
        data = np.float32(img).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
        ret, label, center = cv2.kmeans(
            data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )
        center = np.uint8(center)
        result = center[label.flatten()]
        result = result.reshape(img.shape)
        return result

    def cartoonify_image(self, image):
        if image is None:
            return np.zeros((720, 1280, 3), np.uint8)
        line_size = 7
        blur_value = 7
        edges = self.edge_mask(image, line_size, blur_value)
        total_color = 9
        image = self.color_quantization(image, total_color)
        blurred = cv2.bilateralFilter(image, d=7, sigmaColor=200, sigmaSpace=200)
        image = cv2.bitwise_and(blurred, blurred, mask=edges)
        return image

    def edge_detection(self, image):
        if image is None:
            return np.zeros((720, 1280, 3), np.uint8)
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
        edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)
        return edges

    def contour_detection(self, image):
        if image is None:
            return np.zeros((720, 1280, 3), np.uint8)
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(img_gray, 30, 200)
        contours, hier = cv2.findContours(
            edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        image = cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
        return image

    def process(self, input_data=None):
        image = input_data["image"]
        mode = input_data["mode"]
        processed_image = image
        if mode in self.image_processing_functions:
            processed_image = self.image_processing_functions[mode](image)
        return {
            "processed_image": processed_image,
        }

    def deactivate(self):
        pass
