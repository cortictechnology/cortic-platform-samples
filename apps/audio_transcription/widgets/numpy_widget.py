import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import numpy as np
import styles
from browse_button import BrowseButton
from cortic_platform.sdk.ui.basic_widgets import Label, Container
from cortic_platform.sdk.ui.input_widgets import TextField, DropdownList
from cortic_platform.sdk.ui.chart_widgets import LineChart, Gradient
from cortic_platform.sdk.ui.visualization_utils import *


class NumpyArrayWidget(Container):
    def __init__(self, rect=[0, 0, 450, 500], radius=0, border_color=None, on_event=None):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.background_color = styles.theme_color_content
        self.border_color = styles.theme_color_content
        self.visualization_modes = ["Raw Data", "1D Plot"]
        self.current_visualization_mode = "Raw Data"
        self.data_counter = 0
        self.current_data = None
        self.current_start_domain = 0
        self.current_end_domain = 0
        self.max_data_points = 1000
        self.current_1d_data_points = []
        self.on_selected_numpy_file = on_event

        self.description = Label([(self.rect[2] - styles.input_field_width)/2,
                                  styles.data_widget_subtitle_top_margin,
                                  styles.data_widget_subtitle_width,
                                  styles.data_widget_subtitle_height],
                                 data="Visualize NumPy Array as: ")
        self.description.alignment = "left"
        self.description.font_size = styles.data_widget_subtitle_font_size
        self.description.font_color = styles.font_color

        self.visualization_mode_dropdown = DropdownList(
            [(self.rect[2] - styles.input_field_width)/2 + styles.data_widget_subtitle_width,
             styles.data_widget_dropdown_top_margin,
             styles.data_widget_dropdown_width,
             styles.data_widget_dropdown_height],
            items=self.visualization_modes)
        self.visualization_mode_dropdown.background_color = styles.text_field_color
        self.visualization_mode_dropdown.border_color = styles.text_field_color
        self.visualization_mode_dropdown.focused_field_border_color = styles.text_field_color
        self.visualization_mode_dropdown.corner_radius = 5
        self.visualization_mode_dropdown.label_font_size = 14
        self.visualization_mode_dropdown.label_font_color = styles.font_color
        self.visualization_mode_dropdown.on_widget_event = self.on_dropdown_selected

        self.raw_data_widget = TextField(
            [(self.rect[2] - styles.input_field_width)/2,
             styles.data_widget_dropdown_top_margin * 2 +
             styles.data_widget_dropdown_height,
             styles.input_field_width,
             styles.input_field_height])
        self.raw_data_widget.corner_radius = 10
        self.raw_data_widget.border_color = styles.text_field_color
        self.raw_data_widget.label_text = "Enter or upload your audio data as a Numpy array"
        self.raw_data_widget.hint_text = "Enter or upload your audio data as a Numpy array"
        self.raw_data_widget.input_font_size = 12
        self.raw_data_widget.input_font_color = styles.font_color_dark
        self.raw_data_widget.label_font_size = 12
        self.raw_data_widget.expands = True
        self.raw_data_widget.hint_label_font_size = 12
        self.raw_data_widget.field_background_color = styles.text_field_color

        self.plot_widget_container = Container(
            [(self.rect[2] - styles.input_field_width)/2,
             styles.data_widget_dropdown_top_margin * 2 +
             styles.data_widget_dropdown_height,
             styles.input_field_width,
             styles.input_field_height])
        self.plot_widget_container.corner_radius = 10
        self.plot_widget_container.border_color = styles.text_field_color
        self.plot_widget_container.background_color = styles.text_field_color

        self.plot_widget = LineChart([0, 0, styles.input_field_width, styles.input_field_height])
        self.plot_widget.chart_properties["gradient_type"] = Gradient.Plasma
        self.plot_widget.chart_properties["gradient_orientation"] = "vertical"
        self.plot_widget.start_range = -1
        self.plot_widget.end_range = 1
        self.plot_widget.corner_radius = 10
        self.plot_widget.background = styles.text_field_color
        self.plot_widget.border_color = styles.text_field_color

        self.plot_widget_container.add_child(self.plot_widget)
        self.plot_widget_container.visible = False

        remaining_height = self.rect[3] - \
            (styles.data_widget_dropdown_top_margin * 2 +
                styles.data_widget_dropdown_height +
                styles.input_field_height)

        self.browser_button = BrowseButton(
            [(self.rect[2] - styles.data_widget_browse_button_width)/2,
             self.rect[3] - remaining_height + (remaining_height -
                                                styles.data_widget_browse_button_height)/2,
             styles.data_widget_browse_button_width,
             styles.data_widget_browse_button_height],
             on_event=self.on_selected_numpy_file)

        self.add_children([self.description,
                           self.visualization_mode_dropdown,
                           self.raw_data_widget,
                           self.plot_widget_container,
                           self.browser_button])

    def change_visualization_mode(self, mode):
        if mode == "Raw Data":
            self.raw_data_widget.visible = True
            self.root_widget_tree.update(self.raw_data_widget)
            self.plot_widget_container.visible = False
            self.root_widget_tree.update(self.plot_widget_container)
        elif mode == "1D Plot":
            self.raw_data_widget.visible = False
            self.root_widget_tree.update(self.raw_data_widget)
            self.plot_widget_container.visible = True
            self.root_widget_tree.update(self.plot_widget_container)
        self.current_visualization_mode = mode
        if self.current_data is not None:
            self.set_data(self.current_data)

    def on_dropdown_selected(self, data):
        self.current_visualization_mode = data
        self.change_visualization_mode(data)

    def set_data(self, data):
        self.current_data = data

        data_array = data.flatten().tolist()
        if self.current_visualization_mode == "Raw Data":
            data_array = data_array[:self.max_data_points]
            self.raw_data_widget.set_data(str(data_array) + " ...")
        elif self.current_visualization_mode == "1D Plot":
            min_value = np.min(data_array)
            max_value = np.max(data_array)
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
            self.plot_widget.set_range(min_value, max_value)
            self.plot_widget.set_data([self.current_1d_data_points])

    def get_data(self):
        return self.current_data
