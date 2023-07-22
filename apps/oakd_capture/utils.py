import numpy as np
import cv2
import os
import base64
from cortic_aiot.sdk.app_manager import asyncable
from cortic_aiot.sdk.ui.basic_widgets import Container, Label

def read_asset_image(filename):
    with open(
        os.path.dirname(os.path.realpath(__file__)) + "/assets/" + filename, "rb"
    ) as image_file:
        image = base64.b64encode(image_file.read()).decode("ascii")
    return image


def serialize_frame(frame):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 25]
    _, buffer = cv2.imencode(".jpg", frame, encode_param)
    imgByteArr = base64.b64encode(buffer)
    return imgByteArr.decode("ascii")


def deserialize_frame(frame_data):
    jpg_original = base64.b64decode(frame_data)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    frame = cv2.imdecode(jpg_as_np, flags=1)
    return frame


class MeasurementBar(Container):
    def __init__(
        self, start_x, start_y, width, max_height, radius=0, border_color=None
    ):
        rect = [
            start_x - 25,
            start_y - max_height - 55,
            width + 220,
            max_height + 55 + 55,
        ]
        super().__init__(rect, radius, border_color)
        self.alpha = 0
        outer_rect = [25, 55, width, max_height]
        self.outter_container = Container(outer_rect)
        self.max_height = max_height
        self.outter_container.border_color = "#D9D9D9"
        self.outter_container.border_thickness = 2
        inner_rect = [
            2,
            max_height - self.border_thickness,
            width - self.border_thickness,
            0,
        ]
        self.inner_container = Container(inner_rect)
        self.inner_container.background = "#90EE90"
        self.min_value_label = Label(
            [0, rect[3] - 55, 150, 55],
            alignment="center",
            font_size=40,
            font_color="#ffffff",
            data="0 cm",
        )
        self.max_value_label = Label(
            [0, 0, 150, 55],
            alignment="center",
            font_size=40,
            font_color="#ffffff",
            data="100 cm",
        )
        self.children.append(self.outter_container)
        self.outter_container.children.append(self.inner_container)
        self.children.append(self.min_value_label)
        self.children.append(self.max_value_label)

    def disable(self):
        pass

    def change_height(self, new_height):
        if new_height < 0:
            new_height = 0
        if new_height > self.max_height:
            new_height = self.max_height
        self.inner_container.rect[1] = 2 + (self.max_height - new_height)
        self.inner_container.rect[3] = new_height - self.border_thickness
        self.base_viz_widget.update_widget_appearance(self.inner_container)
