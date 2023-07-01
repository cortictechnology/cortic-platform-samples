import numpy as np
import cv2

supported_functions = ["bilateralFilter", 
                       "blur",
                       "boxFilter",
                       "dilate",
                       "erode",
                       "filter2D",
                       "GaussianBlur",
                       "medianBlur",
                       "Sobel",
                       "stackBlur",
                       "resize",
                       "cvtColor"
                       ]

function_parameters = {
    "bilateralFilter": [15, 75, 75],
    "blur": [(20, 20)],
    "boxFilter": [-1, (10, 10)],
    "dilate": [np.ones((5, 5), np.uint8).tolist()],
    "erode": [np.ones((5, 5), np.uint8).tolist()],
    "filter2D": [-1, (np.ones((5, 5), np.float32)/30).tolist()],
    "GaussianBlur": [(5, 5), 0],
    "medianBlur": [5],
    "Sobel": [cv2.CV_64F, 1, 0, 5],
    "stackBlur": [(5, 5)],
    "resize": [(100, 400)],
    "cvtColor": [cv2.COLOR_BGR2GRAY]
}