from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon, HorizontalSeparator
from cortic_platform.sdk.ui.input_widgets import TabBar
import cv2
import base64
import app_styles
from service_data_widgets import get_data_widget
from utils import *


class ClearButton(Container):
    def __init__(self, rect, background=app_styles.theme_color, radius=0, border_color=None, on_event=None):
        super().__init__(rect, radius, border_color)
        self.alpha = 1
        self.clickable = True
        self.background = background
        self.on_event = on_event

        self.icon = Icon([7, 0, 13, 16],
                         color=app_styles.font_color, data="clear_all")
        self.label = Label([25, 0, 34, 18],
                           font_size=12,
                           alignment="left",
                           font_color=app_styles.font_color,
                           data="Clear")
        self.children.append(self.icon)
        self.children.append(self.label)


class BrowseButton(Container):
    def __init__(self, rect, background=app_styles.theme_color, radius=0, border_color=None, on_event=None):
        super().__init__(rect, radius, border_color)
        self.alpha = 1
        self.clickable = True
        self.background = background
        self.on_event = on_event
        self.for_file_browser = True
        self.icon = Icon([8, 5, 14, 16],
                         color=app_styles.font_color, data="file_settings")
        self.label = Label([27, 5, 50, 18],
                           font_size=13,
                           alignment="left",
                           font_color=app_styles.font_color,
                           data="Browse")
        self.children.append(self.icon)
        self.children.append(self.label)


class IOView(Container):
    def __init__(self, rect, widget_tree, background=app_styles.theme_color, radius=0, border_color=None):
        super().__init__(rect, radius, border_color)
        self.widget_tree = widget_tree
        self.background = background
        self.current_service_inputs = []
        self.current_service_outputs = []
        self.current_input_widgets = {}
        self.current_input_data = {}
        self.current_input_data_numpy = {}
        self.current_input_name = None
        self.current_input_widget = None
        self.current_input_type = None
        self.current_output_widgets = {}
        self.current_output_data = {}
        self.current_output_name = None
        self.current_output_widget = None
        self.current_output_type = None
        self.video_capturers = {}
        self.video_capturers_frame_count = {}
        self.need_disable_input = False
        self.np_input_plot_mode = "raw"
        self.np_output_plot_mode = "raw"

        self.setup_input_container()
        self.setup_output_container()

    def disable_input(self):
        self.need_disable_input = True
        if self.current_input_type == "CvFrame":
            if self.browse_button.visible:
                self.browse_button.visible = False
                self.widget_tree.update(self.browse_button)
        for input_name in self.current_input_widgets:
            data_type = get_data_type(input_name)
            if data_type == "Boolean":
                self.current_input_widgets[input_name].disable_input()
            else:
                self.current_input_widgets[input_name].enable = False
            self.widget_tree.update(self.current_input_widgets[input_name])

    def enable_input(self):
        self.need_disable_input = False
        if self.current_input_type == "CvFrame":
            if not self.browse_button.visible:
                self.browse_button.visible = True
                self.widget_tree.update(self.browse_button)
        for input_name in self.current_input_widgets:
            data_type = get_data_type(input_name)
            if data_type == "Boolean":
                self.current_input_widgets[input_name].enable_input()
            else:
                self.current_input_widgets[input_name].enable = True
            self.widget_tree.update(self.current_input_widgets[input_name])

    def clear_data(self, data):
        self.current_input_widget.clear_data()
        if self.current_input_name in self.current_input_data:
            self.current_input_data[self.current_input_name] = None
        if self.current_input_name in self.current_input_data_numpy:
            del self.current_input_data_numpy[self.current_input_name]
        if self.current_input_name in self.video_capturers:
            self.video_capturers[self.current_input_name].release()
            del self.video_capturers[self.current_input_name]
            del self.video_capturers_frame_count[self.current_input_name]

    def setup_input_container(self):
        self.input_container = Container(
            [38, 34, 481, 582])
        self.input_container.alpha = 1
        self.input_container.radius = 10
        self.input_container.background = app_styles.theme_color_content
        self.input_container.border_color = app_styles.theme_color_content

        self.title = Label([13, 2, 481, 18],
                           font_color=app_styles.font_color_disabled,
                           font_size=12,
                           alignment="left",
                           data="Input")

        self.title_divider = HorizontalSeparator([0, 22, 481, 1],
                                                 color=app_styles.divider_color_2, thickness=1)

        self.input_field_container = Container(
            [24, 83, 433, 285])
        self.input_field_container.background = self.input_container.background
        self.input_field_container.border_color = self.input_container.border_color

        self.default_input_message = Label([0, 83, 433, 285], font_size=15, alignment="center",
                                           font_color=app_styles.font_color_disabled, data="This service does not require any input.")

        self.clear_button = ClearButton(
            [385, 41, 71, 20], background=app_styles.theme_color_highlighted, radius=5, border_color=app_styles.theme_color_highlighted,
            on_event=self.clear_data)

        self.browse_button = BrowseButton(
            [200, 442, 87, 30], background=app_styles.theme_color_highlighted, radius=10, border_color=app_styles.theme_color_highlighted,
            on_event=self.browse_button_callback)
        self.browse_button.visible = False

        self.bottom_divider = HorizontalSeparator([0, 545, 481, 1],
                                                  color=app_styles.divider_color_2, thickness=1)

        self.input_type_bar = TabBar([38, 580, 481, 40],
                                     texts=[],
                                     tooltips=[],
                                     text_size=14,
                                     tab_width=115,
                                     tab_height=38,
                                     label_color=app_styles.font_color,
                                     unselected_label_color=app_styles.font_color_disabled,
                                     indicator_color=app_styles.indicator_color,
                                     use_alternate_style=True)
        self.input_type_bar.on_event = self.on_select_input

        self.input_container.children += [self.title,
                                          self.title_divider, self.bottom_divider, self.input_field_container, self.clear_button, self.browse_button]

        self.children.append(self.input_container)
        self.children.append(self.input_type_bar)

    def setup_output_container(self):
        self.output_container = Container(
            [567, 34, 481, 582])
        self.output_container.alpha = 1
        self.output_container.radius = 10
        self.output_container.background = app_styles.theme_color_content
        self.output_container.border_color = app_styles.theme_color_content

        self.title = Label([13, 2, 481, 18],
                           font_color=app_styles.font_color_disabled,
                           font_size=12,
                           alignment="left",
                           data="Output")

        self.title_divider = HorizontalSeparator([0, 22, 481, 1],
                                                 color=app_styles.divider_color_2, thickness=1)

        self.output_field_container = Container(
            [24, 23, 433, 582-20-40-24])
        self.output_field_container.background = self.output_container.background
        self.output_field_container.border_color = self.output_container.border_color

        self.default_output_message = Label([0, 83, 433, 285], font_size=15, alignment="center",
                                            font_color=app_styles.font_color_disabled, data="This service does not produce any output.")

        self.bottom_divider = HorizontalSeparator([0, 545, 481, 1],
                                                  color=app_styles.divider_color_2, thickness=1)

        self.output_type_bar = TabBar([568, 580, 481, 40],
                                      texts=[],
                                      tooltips=[],
                                      text_size=14,
                                      tab_width=115,
                                      tab_height=38,
                                      label_color=app_styles.font_color,
                                      unselected_label_color=app_styles.font_color_disabled,
                                      indicator_color=app_styles.indicator_color,
                                      use_alternate_style=True)
        self.output_type_bar.on_event = self.on_select_output

        self.output_container.children += [
            self.title, self.title_divider, self.bottom_divider, self.output_field_container]

        self.children.append(self.output_container)
        self.children.append(self.output_type_bar)

    def browse_button_callback(self, data):
        if data != "":
            if data.endswith(".jpg") or data.endswith(".jpeg") or data.endswith(".png") or data.endswith(".bmp"):
                if self.current_input_name in self.video_capturers:
                    self.video_capturers[self.current_input_name].release()
                    del self.video_capturers[self.current_input_name]
                    del self.video_capturers_frame_count[self.current_input_name]
                self.current_input_data_numpy[self.current_input_name] = cv2.imread(
                    data)
                frame_data = self.read_image(data)
                self.current_input_widget.update_image(frame_data)
                self.current_input_data[self.current_input_name] = frame_data
            elif data.endswith(".mp4") or data.endswith(".avi") or data.endswith(".mov"):
                self.video_capturers[self.current_input_name] = cv2.VideoCapture(
                    data)
                self.video_capturers_frame_count[self.current_input_name] = 0
                ret, first_frame = self.video_capturers[self.current_input_name].read(
                )
                if ret:
                    self.video_capturers_frame_count[self.current_input_name] += 1
                    if first_frame.shape[0] > 1000 or first_frame.shape[1] > 560:
                        first_frame = cv2.resize(
                            first_frame, (0, 0), fx=0.5, fy=0.5)
                    frame_data = self.read_cv_frame(first_frame)
                    self.current_input_data_numpy[self.current_input_name] = first_frame
                    self.current_input_widget.update_image(
                        frame_data)
                    self.current_input_data[self.current_input_name] = frame_data

    def get_current_input_data(self):
        input_data = {}
        data_ended = True
        for input_name in self.current_input_data:
            if input_name in self.video_capturers:
                if self.video_capturers_frame_count[input_name] < self.video_capturers[input_name].get(cv2.CAP_PROP_FRAME_COUNT):
                    data_ended = False
                else:
                    self.video_capturers_frame_count[input_name] = 0
                    self.video_capturers[input_name].set(
                        cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.video_capturers[input_name].read()
                if ret:
                    self.video_capturers_frame_count[input_name] += 1
                    if frame.shape[0] > 1000 or frame.shape[1] > 560:
                        frame = cv2.resize(
                            frame, (0, 0), fx=0.5, fy=0.5)
                    frame_data = self.read_cv_frame(frame)
                    input_data[input_name] = frame_data
                    self.current_input_data_numpy[input_name] = frame
                    self.current_input_data[input_name] = frame_data
                    self.current_input_widgets[input_name].update_image(
                        input_data[input_name])
                else:
                    input_data[input_name] = self.read_cv_frame(
                        self.current_input_data_numpy[input_name])
            else:
                input_data[input_name] = self.current_input_data[input_name]
        if len(input_data) == 0:
            data_ended = False
        return input_data, data_ended

    def read_image(self, image_path):
        with open(image_path, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode("ascii")
        return image

    def read_cv_frame(self, frame):
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode("ascii")
        return jpg_as_text

    def refresh_input_widgets(self, on_selected_service=False):
        if on_selected_service:
            self.current_input_data = {}
            self.current_input_data_numpy = {}
            for cap in self.video_capturers:
                self.video_capturers[cap].release()
            self.video_capturers = {}
            self.video_capturers_frame_count = {}
        else:
            for service_input in self.current_input_widgets:
                self.current_input_data[service_input] = self.current_input_widgets[service_input].data
        self.input_type_bar.selected_idx = -1
        self.current_input_widgets = {}
        self.current_input_name = None
        self.current_input_widget = None
        self.current_input_type = None

        self.input_field_container.children = []

        for service_input in self.current_service_inputs:
            input_type = get_data_type(service_input)
            input_widget = get_data_widget(
                input_type, self.input_field_container.rect, service_input[0:service_input.find(
                    "(")], self.widget_tree)
            input_widget.visible = False
            if self.need_disable_input:
                input_widget.enable = False
            if service_input == self.current_service_inputs[0]:
                input_widget.visible = True
                self.current_input_widget = input_widget
                self.current_input_type = input_type
                self.current_input_name = service_input
            self.current_input_widgets[service_input] = input_widget
            if on_selected_service:
                if input_type == "Boolean":
                    self.current_input_data[service_input] = input_widget.data
                else:
                    self.current_input_data[service_input] = None
            else:
                if service_input in self.current_input_data:
                    input_widget.data = self.current_input_data[service_input]
            self.input_field_container.children.append(input_widget)
        if self.current_input_type == "CvFrame":
            if not self.need_disable_input:
                self.browse_button.visible = True
        else:
            if self.browse_button.visible:
                self.browse_button.visible = False
        if on_selected_service:
            self.widget_tree.update(self.browse_button)

        if len(self.input_field_container.children) == 0:
            self.input_field_container.children.append(
                self.default_input_message)
            self.clear_button.visible = False
            self.widget_tree.update(self.clear_button)
        else:
            if not self.clear_button.visible:
                self.clear_button.visible = True
                self.widget_tree.update(self.clear_button)

    def refresh_output_widgets(self, on_selected_service=False):
        if on_selected_service:
            self.current_output_data = {}
            self.current_output_data_numpy = {}

        else:
            for service_output in self.current_output_widgets:
                self.current_output_data[service_output] = self.current_output_widgets[service_output].data
        self.output_type_bar.selected_idx = -1
        self.current_output_widgets = {}
        self.current_output_name = None
        self.current_output_widget = None
        self.current_output_type = None

        self.output_field_container.children = []

        for service_output in self.current_service_outputs:
            output_type = get_data_type(service_output)
            output_widget = get_data_widget(
                output_type, self.output_field_container.rect, service_output[0:service_output.find("(")], self.widget_tree, for_output=True)
            output_widget.visible = False
            if service_output == self.current_service_outputs[0]:
                output_widget.visible = True
                self.current_output_widget = output_widget
                self.current_output_type = output_type
                self.current_output_name = service_output
            self.current_output_widgets[service_output] = output_widget
            if on_selected_service:
                self.current_output_data[service_output] = None
                if output_type == "NumpyArray":
                    output_widget.data_counter = 0
            else:
                if service_output in self.current_output_data:
                    output_widget.data = self.current_output_data[service_output]
                else:
                    self.current_output_data[service_output] = None
            self.output_field_container.children.append(output_widget)

        if len(self.output_field_container.children) == 0:
            self.output_field_container.children.append(
                self.default_output_message)

    def on_select_input(self, selected_idx):
        input_name = self.current_service_inputs[selected_idx]
        if self.current_input_widget != None:
            if self.current_input_name != input_name:
                self.current_input_data[self.current_input_name] = self.current_input_widget.data
                self.current_input_widget.visible = False
                self.widget_tree.update(self.current_input_widget)
                self.current_input_name = input_name
                self.current_input_type = get_data_type(input_name)
                self.current_input_widget = self.current_input_widgets[input_name]
                self.current_input_widget.visible = True
                self.widget_tree.update(self.current_input_widget)
                if self.current_input_type == "CvFrame":
                    if not self.need_disable_input:
                        self.browse_button.visible = True
                        self.widget_tree.update(self.browse_button)
                else:
                    if self.browse_button.visible:
                        self.browse_button.visible = False
                        self.widget_tree.update(self.browse_button)
                if self.current_input_data[self.current_input_name] is not None:
                    self.current_input_widget.data = self.current_input_data[self.current_input_name]

    def on_select_output(self, selected_idx):
        output_name = self.current_service_outputs[selected_idx]
        if self.current_output_widget != None:
            if self.current_output_name != output_name:
                self.current_output_data[self.current_output_name] = self.current_output_widget.data
                self.current_output_widget.visible = False
                self.widget_tree.update(self.current_output_widget)
                self.current_output_name = output_name
                self.current_output_type = get_data_type(output_name)
                self.current_output_widget = self.current_output_widgets[output_name]
                self.current_output_widget.visible = True
                self.widget_tree.update(self.current_output_widget)
                if self.current_output_data[self.current_output_name] is not None:
                    self.current_output_widget.data = self.current_output_data[
                        self.current_output_name]

    def update(self, service_data, on_selected_service=True):
        if self.current_input_widget != None:
            self.current_input_widget.visible = False
            self.widget_tree.update(self.current_input_widget)
        if self.current_output_widget != None:
            self.current_output_widget.visible = False
            self.widget_tree.update(self.current_output_widget)
        if service_data is None:
            return
        self.current_service_inputs = get_service_input_list(service_data)
        self.current_service_outputs = get_service_output_list(service_data)
        self.refresh_input_widgets(on_selected_service=on_selected_service)
        self.refresh_output_widgets(on_selected_service=on_selected_service)
        self.input_type_bar.texts = self.current_service_inputs
        self.input_type_bar.tooltips = self.current_service_inputs
        self.output_type_bar.texts = self.current_service_outputs
        self.output_type_bar.tooltips = self.current_service_outputs
        self.widget_tree.update(self.input_field_container)
        self.widget_tree.update(self.input_type_bar)
        self.widget_tree.update(self.output_field_container)
        self.widget_tree.update(self.output_type_bar)
