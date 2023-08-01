from cortic_platform.sdk.ui.basic_widgets import Image, Label, Container
from cortic_platform.sdk.ui.input_widgets import TextField, Toggle, DropdownMenu
from cortic_platform.sdk.ui.misc_widgets import LivePlot
import app_styles
import numpy as np


class BooleanWidget(Container):
    def __init__(self, rect, data_name, radius=0, border_color=None, on_event=None):
        super().__init__(rect, radius, border_color)
        self.background = app_styles.theme_color_content
        self.border_color = app_styles.theme_color_content
        self.data_name = data_name

        self.children.append(Label([0, 0, rect[2], 21],
                                   data="Choose a Boolean value for " + self.data_name,
                                   alignment="center",
                                   font_size=14,
                                   font_color=app_styles.font_color))
        self.toggle = Toggle([0, 31, rect[2], app_styles.single_line_input_widget_height],
                             active_color=app_styles.button_color)
        self.toggle.on_event = self.on_toggle
        self.data = self.toggle.data
        self.children.append(self.toggle)

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
        super().__init__(rect, radius, border_color)
        self.background = app_styles.theme_color_content
        self.border_color = app_styles.theme_color_content
        self.visualization_modes = ["Raw Data", "1D Plot"]
        self.current_visualization_mode = "Raw Data"
        self.for_output = for_output
        self.widget_tree = widget_tree
        self.data_counter = 0

        self.description = Label([0, 3, 170, 20],
                                 data="Visualize NumPy Array as: ",
                                 alignment="left",
                                 font_size=12,
                                 font_color=app_styles.font_color)

        self.visualization_mode_dropdown = DropdownMenu([170, 0, 121, 25],
                                                        font_size=14,
                                                        font_color=app_styles.font_color,
                                                        data_list=self.visualization_modes)
        self.visualization_mode_dropdown.background = app_styles.item_color_1
        self.visualization_mode_dropdown.border_color = app_styles.item_color_1
        self.visualization_mode_dropdown.radius = 5
        self.visualization_mode_dropdown.on_event = self.on_dropdown_selected

        if self.for_output:
            self.raw_data_widget = Label([0, 53, rect[2], app_styles.multiple_line_input_widget_height],
                                         data="",
                                         alignment="left",
                                         font_size=16,
                                         font_color=app_styles.font_color,
                                         paddings=[20, 20, 0, 0])
            self.raw_data_widget.alpha = 1
            self.raw_data_widget.radius = 10
            self.raw_data_widget.border_color = app_styles.text_field_color
            self.raw_data_widget.background = app_styles.text_field_color
            self.raw_data_widget.scrollable = True
        else:
            self.raw_data_widget = TextField([0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04],
                                             "Enter a Numpy Array in list from",
                                             "Enter a Numpy Array in list from",
                                             font_size=16,
                                             font_color=app_styles.font_color,
                                             label_font_size=16,
                                             expands=True,
                                             float_label_font_size=12,
                                             fill_color=app_styles.text_field_color,
                                             )
            self.raw_data_widget.radius = 10
            self.raw_data_widget.border_color = app_styles.text_field_color

        self.plot_widget_container = Container([0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04],
                                               radius=10,
                                               background=app_styles.text_field_color,
                                               border_color=app_styles.text_field_color)
        self.plot_widget = LivePlot([0, 0, rect[2], app_styles.multiple_line_input_widget_height*1.04],
                                    "value",
                                    data=[],
                                    min_value=0,
                                    max_value=1,
                                    limit_count=22400,
                                    line_thickness=2,
                                    palette=[app_styles.button_color])
        self.plot_widget.radius = 10
        self.plot_widget.background = app_styles.text_field_color
        self.plot_widget.border_color = app_styles.text_field_color

        self.plot_widget_container.children.append(self.plot_widget)
        self.plot_widget_container.visible = False

        if self.for_output:
            self.children += [self.description, self.visualization_mode_dropdown,
                              self.raw_data_widget, self.plot_widget_container]
        else:
            self.children += [self.raw_data_widget]

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

    def on_dropdown_selected(self, data):
        self.current_visualization_mode = data
        self.change_visualization_mode(data)

    def set_data(self, data):
        if self.current_visualization_mode == "Raw Data":
            self.raw_data_widget.data = str(data)
        elif self.current_visualization_mode == "1D Plot":
            data_array = np.array(data).flatten().tolist()
            data_points = []
            for i in range(len(data_array)):
                data_point = [0, self.data_counter, data_array[i]]
                data_points.append(data_point)
                self.data_counter += 1
            self.plot_widget.data = data_points


def get_data_widget(data_type, rect, data_name, widget_tree, for_output=False):
    if data_type == "CvFrame":
        widget = Image([0, 0, rect[2], rect[3]],
                       scaling_method="fit")
        widget.radius = 10
        return widget
    elif data_type == "NumpyArray":
        return NumpyArrayWidget([0, 0, rect[2], rect[3]], widget_tree, for_output=for_output)
    elif data_type == "Int":
        widget = TextField([0, 113, rect[2],  app_styles.single_line_input_widget_height*1.2],
                           "Enter an Integer",
                           "Enter an Integer",
                           font_size=16,
                           font_color=app_styles.font_color,
                           label_font_size=16,
                           expands=False,
                           float_label_font_size=12,
                           fill_color=app_styles.text_field_color,
                           input_alignment="center"
                           )
        widget.radius = 8
        widget.border_color = app_styles.text_field_color
        if for_output:
            widget = Label([0, 120, rect[2],  app_styles.single_line_input_widget_height],
                           data="",
                           alignment="center",
                           font_size=16,
                           font_color=app_styles.font_color)
            widget.alpha = 1
            widget.radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background = app_styles.text_field_color
            widget.scrollable = True
        return widget
    elif data_type == "Float":
        widget = TextField([0, 113, rect[2],  app_styles.single_line_input_widget_height*1.2],
                           "Enter a Float Number",
                           "Enter a Float Number",
                           font_size=16,
                           font_color=app_styles.font_color,
                           label_font_size=16,
                           expands=False,
                           float_label_font_size=12,
                           fill_color=app_styles.text_field_color,
                           input_alignment="center"
                           )
        widget.radius = 8
        widget.border_color = app_styles.text_field_color
        if for_output:
            widget = Label([0, 120, rect[2],  app_styles.single_line_input_widget_height],
                           data="",
                           alignment="center",
                           font_size=16,
                           font_color=app_styles.font_color)
            widget.alpha = 1
            widget.radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background = app_styles.text_field_color
            widget.scrollable = True
        return widget
    elif data_type == "String":
        widget = TextField([0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04],
                           "Enter a String",
                           "Enter a String",
                           font_size=16,
                           font_color=app_styles.font_color,
                           label_font_size=16,
                           expands=True,
                           float_label_font_size=12,
                           fill_color=app_styles.text_field_color,
                           )
        widget.radius = 10
        widget.border_color = app_styles.text_field_color

        if for_output:
            widget = Label([0, 53, rect[2], app_styles.multiple_line_input_widget_height],
                           data="",
                           alignment="left",
                           font_size=16,
                           font_color=app_styles.font_color,
                           paddings=[20, 20, 0, 0])
            widget.alpha = 1
            widget.radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background = app_styles.text_field_color
            widget.scrollable = True
        return widget
    elif data_type == "Boolean":
        return BooleanWidget([0, (rect[3] - 76)/2, rect[2], 86], data_name)
    elif data_type == "List":
        widget = TextField([0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04],
                           "Enter a list of serializable data",
                           "Enter a list of serializable data",
                           font_size=16,
                           font_color=app_styles.font_color,
                           label_font_size=16,
                           expands=True,
                           float_label_font_size=12,
                           fill_color=app_styles.text_field_color,
                           )
        widget.radius = 10
        widget.border_color = app_styles.text_field_color
        if for_output:
            widget = Label([0, 53, rect[2], app_styles.multiple_line_input_widget_height],
                           data="",
                           alignment="left",
                           font_size=16,
                           font_color=app_styles.font_color,
                           paddings=[20, 20, 0, 0])
            widget.alpha = 1
            widget.radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background = app_styles.text_field_color
            widget.scrollable = True
        return widget
    elif data_type == "Json":
        widget = TextField([0, 46, rect[2], app_styles.multiple_line_input_widget_height*1.04],
                           "Enter a JSON serializable dictionary",
                           "Enter a JSON serializable dictionary",
                           font_size=16,
                           font_color=app_styles.font_color,
                           label_font_size=16,
                           expands=True,
                           float_label_font_size=12,
                           fill_color=app_styles.text_field_color,
                           )
        widget.radius = 10
        widget.border_color = app_styles.text_field_color
        if for_output:
            widget = Label([0, 53, rect[2], app_styles.multiple_line_input_widget_height],
                           data="",
                           alignment="left",
                           font_size=16,
                           font_color=app_styles.font_color,
                           paddings=[20, 20, 0, 0])
            widget.alpha = 1
            widget.radius = 10
            widget.border_color = app_styles.text_field_color
            widget.background = app_styles.text_field_color
            widget.scrollable = True
        return widget
    else:
        return Container([0, 0, rect[2], rect[3]])
