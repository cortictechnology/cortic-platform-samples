from cortic_platform.sdk.ui.basic_widgets import Image, Label, Container
from cortic_platform.sdk.ui.input_widgets import TextField, Toggle, DropdownList
from cortic_platform.sdk.ui.chart_widgets import LineChart, Gradient
from cortic_platform.sdk.ui.visualization_utils import *
import app_styles
import numpy as np


class BooleanWidget(Container):
    def __init__(self, rect, data_name, radius=0, border_color=None, on_event=None):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.background_color = app_styles.theme_color_content
        self.border_color = app_styles.theme_color_content
        self.data_name = data_name

        hint_label = Label([0, 0, rect[2], 21],
                           data="Choose a Boolean value for " + self.data_name)
        hint_label.alignment = "center"
        hint_label.font_size = 12
        hint_label.font_color = app_styles.font_color

        self.add_child(hint_label)

        self.toggle = Toggle(
            [0, 31, rect[2], app_styles.single_line_input_widget_height])
        self.toggle.active_color = app_styles.button_color
        self.toggle.on_widget_event = self.on_toggle

        self.data = self.toggle.data
        self.add_child(self.toggle)

    def on_toggle(self, data):
        self.data = data

    def enable_input(self):
        self.toggle.enable = True

    def disable_input(self):
        self.toggle.enable = False

    def clear_data(self):
        self.toggle.clear_data()


class NumpyArrayWidget(Container):
    def __init__(self, rect, widget_tree, radius=0, border_color=None, on_event=None, for_output=False):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.background_color = app_styles.theme_color_content
        self.border_color = app_styles.theme_color_content
        self.visualization_modes = ["Raw Data", "1D Plot"]
        self.current_visualization_mode = "Raw Data"
        self.for_output = for_output
        self.widget_tree = widget_tree
        self.data_counter = 0
        self.current_data = None
        self.current_start_domain = 0
        self.current_end_domain = 0
        self.max_data_points = 200
        self.current_1d_data_points = []

        self.description = Label([0, 16, 170, 20],
                                 data="Visualize NumPy Array as: ")
        self.description.alignment = "left"
        self.description.font_size = 12
        self.description.font_color = app_styles.font_color

        self.visualization_mode_dropdown = DropdownList(
            [170, 13, 121, 25], items=self.visualization_modes)
        self.visualization_mode_dropdown.background_color = app_styles.item_color_1
        self.visualization_mode_dropdown.border_color = app_styles.item_color_1
        self.visualization_mode_dropdown.corner_radius = 5
        self.visualization_mode_dropdown.label_font_size = 14
        self.visualization_mode_dropdown.label_font_color = app_styles.font_color
        self.visualization_mode_dropdown.on_widget_event = self.on_dropdown_selected

        if self.for_output:
            self.raw_data_widget = Label(
                [0, 60, rect[2], rect[3] - 60], data="")
            self.raw_data_widget.alignment = "left"
            self.raw_data_widget.font_size = 12
            self.raw_data_widget.font_color = app_styles.font_color_dark
            self.raw_data_widget.paddings = [20, 20, 0, 0]
            self.raw_data_widget.alpha = 1
            self.raw_data_widget.corner_radius = 10
            self.raw_data_widget.border_color = app_styles.text_field_color
            self.raw_data_widget.background_color = app_styles.text_field_color
            self.raw_data_widget.scrollable = True
        else:
            self.raw_data_widget = TextField(
                [0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04])
            self.raw_data_widget.corner_radius = 10
            self.raw_data_widget.border_color = app_styles.text_field_color
            self.raw_data_widget.label_text = "Enter a Numpy Array in list from"
            self.raw_data_widget.hint_text = "Enter a Numpy Array in list from"
            self.raw_data_widget.input_font_size = 12
            self.raw_data_widget.input_font_color = app_styles.font_color_dark
            self.raw_data_widget.label_font_size = 12
            self.raw_data_widget.expands = True
            self.raw_data_widget.hint_label_font_size = 12
            self.raw_data_widget.field_background_color = app_styles.text_field_color

        self.plot_widget_container = Container([0, 52, rect[2], rect[3] - 60])
        self.plot_widget_container.corner_radius = 10
        self.plot_widget_container.border_color = app_styles.text_field_color
        self.plot_widget_container.background_color = app_styles.text_field_color

        self.plot_widget = LineChart([0, 0, rect[2], rect[3]])
        self.plot_widget.chart_properties["gradient_type"] = Gradient.Plasma
        self.plot_widget.chart_properties["gradient_orientation"] = "vertical"
        self.plot_widget.start_range = -1
        self.plot_widget.end_range = 1
        self.plot_widget.corner_radius = 10
        self.plot_widget.background = app_styles.text_field_color
        self.plot_widget.border_color = app_styles.text_field_color

        self.plot_widget_container.add_child(self.plot_widget)
        self.plot_widget_container.visible = False

        if self.for_output:
            self.add_children([self.description, self.visualization_mode_dropdown,
                              self.raw_data_widget, self.plot_widget_container])
        else:
            self.add_child(self.raw_data_widget)

    def change_visualization_mode(self, mode):
        if mode == "Raw Data":
            self.raw_data_widget.visible = True
            self.widget_tree.update(self.raw_data_widget)
            self.plot_widget_container.visible = False
            self.widget_tree.update(self.plot_widget_container)
        elif mode == "1D Plot":
            self.raw_data_widget.visible = False
            self.widget_tree.update(self.raw_data_widget)
            self.plot_widget_container.visible = True
            self.widget_tree.update(self.plot_widget_container)
        self.current_visualization_mode = mode
        if self.current_data is not None:
            self.set_data(self.current_data)

    def on_dropdown_selected(self, data):
        self.current_visualization_mode = data
        self.change_visualization_mode(data)

    def set_data(self, data):
        self.current_data = data
        if self.current_visualization_mode == "Raw Data":
            self.raw_data_widget.data = str(data)
        elif self.current_visualization_mode == "1D Plot":
            data_array = np.array(data).flatten().tolist()
            for i in range(len(data_array)):
                data_point = [self.data_counter,
                              data_array[i]]
                self.current_1d_data_points.append(data_point)
                if len(self.current_1d_data_points) > self.max_data_points:
                    self.current_1d_data_points.pop(0)
                self.data_counter += 1
            if len(self.current_1d_data_points) > 0:
                self.current_start_domain = self.current_1d_data_points[0][0]
                self.current_end_domain = self.current_1d_data_points[-1][0]
            self.plot_widget.set_domain(
                self.current_start_domain, self.current_end_domain)
            self.plot_widget.set_data([self.current_1d_data_points])


class ListWidget(Container):
    def __init__(self, rect, widget_tree, radius=0, border_color=None, on_event=None, for_output=False):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.background_color = app_styles.theme_color_content
        self.border_color = app_styles.theme_color_content
        self.visualization_modes = [
            "Raw Data",
            "Face Detection",
            "Face Mesh",
            "Object Detection",
            "Hand Landmarks",
            "Pose Landmarks",
            "Segmentation Mask"]
        self.current_visualization_mode = "Raw Data"
        self.data_counter = 0
        self.for_output = for_output
        self.widget_tree = widget_tree
        self.current_data = None
        self.current_input_images = None
        self.current_input_name = None
        self.visualization_functions = {
            "Face Detection": draw_face_detection,
            "Face Mesh": draw_face_mesh,
            "Object Detection": draw_object_detection,
            "Hand Landmarks": draw_hand_landmarks,
            "Pose Landmarks": draw_body_landmarks,
            "Segmentation Mask": draw_masks
        }

        self.description = Label([0, 16, 170, 20],
                                 data="Visualize List Data as: ")
        self.description.alignment = "left"
        self.description.font_size = 12
        self.description.font_color = app_styles.font_color

        self.visualization_mode_dropdown = DropdownList(
            [140, 13, 170, 25], items=self.visualization_modes)
        self.visualization_mode_dropdown.background_color = app_styles.item_color_1
        self.visualization_mode_dropdown.border_color = app_styles.item_color_1
        self.visualization_mode_dropdown.corner_radius = 5
        self.visualization_mode_dropdown.label_font_size = 12
        self.visualization_mode_dropdown.label_font_color = app_styles.font_color
        self.visualization_mode_dropdown.on_widget_event = self.on_dropdown_selected

        if self.for_output:
            self.raw_data_widget = Label([0, 60, rect[2], rect[3]-24],
                                         data="")
            self.raw_data_widget.alpha = 1
            self.raw_data_widget.corner_radius = 10
            self.raw_data_widget.border_color = app_styles.text_field_color
            self.raw_data_widget.background_color = app_styles.text_field_color
            self.raw_data_widget.scrollable = True
            self.raw_data_widget.alignment = "left"
            self.raw_data_widget.font_size = 12
            self.raw_data_widget.font_color = app_styles.font_color_dark
            self.raw_data_widget.paddings = [20, 20, 0, 0]
        else:
            self.raw_data_widget = TextField(
                [0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04])
            self.raw_data_widget.corner_radius = 10
            self.raw_data_widget.border_color = app_styles.text_field_color
            self.raw_data_widget.label_text = "Enter a list of serializable data"
            self.raw_data_widget.hint_text = "Enter a list of serializable data"
            self.raw_data_widget.input_font_size = 12
            self.raw_data_widget.input_font_color = app_styles.font_color_dark
            self.raw_data_widget.label_font_size = 12
            self.raw_data_widget.expands = True
            self.raw_data_widget.hint_label_font_size = 12
            self.raw_data_widget.field_background_color = app_styles.text_field_color

        self.image_widget = Image([0, 60, 433, 285])
        self.image_widget.scaling_mode = "fit"
        self.image_widget.corner_radius = 10
        self.image_widget.visible = False

        if self.for_output:
            self.add_children([self.description, self.visualization_mode_dropdown,
                              self.raw_data_widget, self.image_widget])
        else:
            self.add_child(self.raw_data_widget)

    def change_visualization_mode(self, mode):
        if mode == "Raw Data":
            self.raw_data_widget.visible = True
            self.widget_tree.update(self.raw_data_widget)
            self.image_widget.visible = False
            self.widget_tree.update(self.image_widget)
        else:
            self.raw_data_widget.visible = False
            self.widget_tree.update(self.raw_data_widget)
            self.image_widget.visible = True
            self.widget_tree.update(self.image_widget)
        self.current_visualization_mode = mode
        if self.current_data is not None:
            self.set_data(self.current_data,
                          self.current_input_images, self.current_input_name)

    def on_dropdown_selected(self, data):
        self.current_visualization_mode = data
        self.change_visualization_mode(data)

    def set_data(self, data, input_images={}, input_name=""):
        self.current_data = data
        self.current_input_images = input_images
        self.current_input_name = input_name
        if self.current_visualization_mode == "Raw Data":
            self.raw_data_widget.data = str(data)
        else:
            if input_name in input_images:
                input_image = input_images[input_name]
                annotated_image = input_image.copy()
                annotated_image = encode_jpeg(self.visualization_functions[self.current_visualization_mode](
                    annotated_image, data))
                self.image_widget.set_data(annotated_image)


def get_data_widget(data_type, rect, data_name, widget_tree, for_output=False):
    if data_type == "CvFrame":
        widget = Image([0, 0, rect[2], rect[3]])
        widget.corner_radius = 10
        if for_output:
            widget = Image([0, 60, 433, 285])
            widget.corner_radius = 10
        return widget
    elif data_type == "NumpyArray":
        return NumpyArrayWidget([0, 0, rect[2], rect[3]], widget_tree, for_output=for_output)
    elif data_type == "Int":
        widget = TextField(
            [0, 113, rect[2],  app_styles.single_line_input_widget_height*1.2])
        widget.corner_radius = 8
        widget.border_color = app_styles.text_field_color
        widget.label_text = "Enter an Integer"
        widget.hint_text = "Enter an Integer"
        widget.input_font_size = 12
        widget.input_font_color = app_styles.font_color_dark
        widget.label_font_size = 12
        widget.expands = False
        widget.hint_label_font_size = 12
        widget.field_background_color = app_styles.text_field_color
        widget.input_alignment = "center"

        if for_output:
            widget = Label([0, (rect[3] - app_styles.single_line_input_widget_height)/2, rect[2],  app_styles.single_line_input_widget_height],
                           data="")
            widget.alpha = 1
            widget.corner_radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background_color = app_styles.text_field_color
            widget.scrollable = True
            widget.alignment = "center"
            widget.font_size = 12
            widget.font_color = app_styles.font_color_dark

        return widget
    elif data_type == "Float":
        widget = TextField(
            [0, 113, rect[2],  app_styles.single_line_input_widget_height*1.2])
        widget.corner_radius = 8
        widget.border_color = app_styles.text_field_color
        widget.label_text = "Enter a Float Number"
        widget.hint_text = "Enter a Float Number"
        widget.input_font_size = 12
        widget.input_font_color = app_styles.font_color_dark
        widget.label_font_size = 12
        widget.expands = False
        widget.hint_label_font_size = 12
        widget.field_background_color = app_styles.text_field_color
        widget.input_alignment = "center"

        if for_output:
            widget = Label([0, (rect[3] - app_styles.single_line_input_widget_height)/2, rect[2],  app_styles.single_line_input_widget_height],
                           data="")
            widget.alpha = 1
            widget.corner_radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background_color = app_styles.text_field_color
            widget.scrollable = True
            widget.alignment = "center"
            widget.font_size = 12
            widget.font_color = app_styles.font_color_dark

        return widget
    elif data_type == "String":
        widget = TextField(
            [0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04])
        widget.corner_radius = 10
        widget.border_color = app_styles.text_field_color
        widget.input_alignment = "left"
        widget.label_text = "Enter a String"
        widget.hint_text = "Enter a String"
        widget.input_font_size = 12
        widget.input_font_color = app_styles.font_color_dark
        widget.label_font_size = 12
        widget.expands = True
        widget.hint_label_font_size = 12
        widget.field_background_color = app_styles.text_field_color

        if for_output:
            widget = Label([0, 24, rect[2], rect[3]-24],
                           data="")
            widget.alpha = 1
            widget.corner_radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background_color = app_styles.text_field_color
            widget.scrollable = True
            widget.alignment = "left"
            widget.font_size = 12
            widget.font_color = app_styles.font_color_dark
            widget.paddings = [20, 20, 0, 0]

        return widget
    elif data_type == "Boolean":
        return BooleanWidget([0, (rect[3] - 86)/2, rect[2], 86], data_name)
    elif data_type == "List":
        return ListWidget([0, 0, rect[2], rect[3]],
                          widget_tree, for_output=for_output)
    elif data_type == "Json":
        widget = TextField(
            [0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04])
        widget.corner_radius = 10
        widget.border_color = app_styles.text_field_color
        widget.label_text = "Enter a JSON serializable dictionary"
        widget.hint_text = "Enter a JSON serializable dictionary"
        widget.input_font_size = 12
        widget.input_font_color = app_styles.font_color_dark
        widget.label_font_size = 12
        widget.expands = True
        widget.hint_label_font_size = 12
        widget.field_background_color = app_styles.text_field_color

        if for_output:
            widget = Label([0, 24, rect[2], rect[3]-24],
                           data="")
            widget.alpha = 1
            widget.corner_radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background_color = app_styles.text_field_color
            widget.scrollable = True
            widget.alignment = "left"
            widget.font_size = 12
            widget.font_color = app_styles.font_color_dark
            widget.paddings = [20, 20, 0, 0]

        return widget
    else:
        return Container([0, 0, rect[2], rect[3]])
