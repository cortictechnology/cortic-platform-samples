from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon, VerticalSeparator
from cortic_platform.sdk.ui.input_widgets import ListItem, ListView, Button
from utils import *
import app_styles
import time
from cortic_platform.sdk.service_data_types import STATE_DATA_TYPES


class StatesView(Container):
    def __init__(self, rect, widget_tree, show_state_editor, background=app_styles.theme_color, radius=0, border_color=None):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.states = {}
        self.state_types = {}
        self.need_disable_input = False
        self.widget_tree = widget_tree
        self.show_state_editor = show_state_editor
        self.list_items = []
        self.background_color = background
        self.current_service_key = None

        self.item_backgrounds = [
            app_styles.item_color_3, app_styles.item_color_1]

        self.listview_container = Container([6, 6, 572, 635])
        self.listview_container.corner_radius = 10
        self.listview_container.background_color = app_styles.theme_color_content
        self.listview_container.border_color = app_styles.theme_color_content

        self.listview_title_bar = Container([0, 0, 572, 54])
        self.listview_title_bar.background_color = app_styles.item_color_1
        self.listview_title_bar.border_color = app_styles.item_color_1
        self.listview_title_bar.custom_corner_radius = [10, 10, 0, 0]
        self.listview_title_bar.use_custom_corner_radius = True

        self.listview_title_name = Label([31, 15, 100, 25],
                                         data="State Name")
        self.listview_title_name.alignment = "center"
        self.listview_title_name.font_weight = "bold"
        self.listview_title_name.font_size = 12
        self.listview_title_name.font_color = app_styles.font_color

        self.listview_title_type = Label([178, 15, 100, 25],
                                         data="State Type")
        self.listview_title_type.alignment = "center"
        self.listview_title_type.font_weight = "bold"
        self.listview_title_type.font_size = 12
        self.listview_title_type.font_color = app_styles.font_color

        self.listview_title_value = Label([316, 15, 100, 25],
                                          data="State Value")
        self.listview_title_value.alignment = "center"
        self.listview_title_value.font_weight = "bold"
        self.listview_title_value.font_size = 12
        self.listview_title_value.font_color = app_styles.font_color

        self.listview_title_bar.add_children([self.listview_title_name,
                                             self.listview_title_type,
                                             self.listview_title_value])

        self.add_state_button = Button([512, 11, 30, 30])
        self.add_state_button.label = "+"
        self.add_state_button.button_color = app_styles.item_color_1
        self.add_state_button.label_font_color = app_styles.font_color_dark
        self.add_state_button.label_font_size = 20
        self.add_state_button.on_widget_event = self.on_add_state
        self.add_state_button.corner_radius = 0

        self.add_state_divider = VerticalSeparator([510, 20, 1, 14])
        self.add_state_divider.line_color = app_styles.divider_color_3
        self.add_state_divider.thickness = 1

        self.remove_state_button = Button([544, 11, 30, 30])
        self.remove_state_button.label = "-"
        self.remove_state_button.button_color = app_styles.item_color_1
        self.remove_state_button.label_font_color = app_styles.font_color_dark
        self.remove_state_button.label_font_size = 20
        self.remove_state_button.on_widget_event = self.on_remove_state
        self.remove_state_button.corner_radius = 0

        self.remove_state_divider = VerticalSeparator([542, 20, 1, 14])
        self.remove_state_divider.line_color = app_styles.divider_color_3
        self.remove_state_divider.thickness = 1

        self.listview_container.add_children([self.listview_title_bar,
                                              #  self.add_state_divider,
                                              #  self.add_state_button, self.remove_state_button,
                                              #  self.remove_state_divider
                                              ])

        self.add_child(self.listview_container)

        self.build_states()

    def on_add_state(self, data):
        self.show_state_editor("Add", "Enter the details of the new state")

    def on_edit_state(self, data):
        state_name = list(self.states[self.current_service_key].keys())[data]
        state_value = str(self.states[self.current_service_key][state_name])
        state_type = STATE_DATA_TYPES.index(
            self.state_types[self.current_service_key][state_name])
        self.show_state_editor("Edit", "Edit the details of the state", state_name=state_name,
                               state_value=state_value, state_type=state_type)

    def on_remove_state(self, data):
        if self.listview.selected_idx >= 0:
            key_to_delete = list(self.states[self.current_service_key].keys())[
                self.listview.selected_idx]
            del self.states[self.current_service_key][key_to_delete]
            del self.state_types[self.current_service_key][key_to_delete]
            self.update_states()

    def create_state_list_items(self):
        self.list_items = []
        counter = 0
        if self.current_service_key is not None:
            for state in self.states[self.current_service_key]:
                background = self.item_backgrounds[counter % 2]
                state_label = Label([0, 0, 170, 54], data=state)
                state_label.alpha = 1
                state_label.border_color = background
                state_label.background_color = background
                state_label.font_size = 13
                state_label.font_color = app_styles.font_color_dark
                state_label.alignment = "left"
                state_label.paddings = [42, 15, 0, 0]
                state_label.enable_markdown = False
                state_label.highlighted_font_color = app_styles.font_color
                state_type = Label(
                    [0, 0, 113, 54], data=self.state_types[self.current_service_key][state])
                state_type.alpha = 1
                state_type.border_color = background
                state_type.background_color = background
                state_type.font_size = 13
                state_type.font_color = app_styles.font_color_dark
                state_type.alignment = "center"
                state_type.enable_markdown = False
                state_type.highlighted_font_color = app_styles.font_color

                state_value = Label([0, 0, 167, 54], data=str(
                    self.states[self.current_service_key][state]))
                state_value.alpha = 1
                state_value.border_color = background
                state_value.background_color = background
                state_value.font_size = 13
                state_value.font_color = app_styles.font_color_dark
                state_value.alignment = "center"
                state_value.enable_markdown = False
                state_value.highlighted_font_color = app_styles.font_color

                divider = Label([0, 0, 48, 54], data="")
                divider.alpha = 1
                divider.border_color = background
                divider.background_color = background
                divider.font_size = 13
                divider.font_color = app_styles.font_color_dark
                divider.alignment = "center"
                divider.enable_markdown = False
                divider.highlighted_font_color = app_styles.font_color

                edit_icon = Icon([0, 0, 40, 54], data="pencil")
                edit_icon.on_widget_event = self.on_edit_state
                edit_icon.capture_mouse_event = True
                edit_icon.alpha = 1
                edit_icon.border_color = background
                edit_icon.background_color = background
                edit_icon.icon_color = app_styles.font_color_dark
                edit_icon.icon_size = 16
                edit_icon.highlighted_icon_color = app_styles.font_color

                edit_icon.on_event = self.on_edit_state
                edit_icon.clickable = True
                edit_icon.alpha = 1
                edit_icon.border_color = background
                edit_icon.background = background

                ender = Label([0, 0, 32, 54], data="")
                ender.alpha = 1
                ender.border_color = background
                ender.background_color = background
                ender.font_size = 13
                ender.font_color = app_styles.font_color_dark
                ender.alignment = "center"
                ender.enable_markdown = False
                ender.highlighted_font_color = app_styles.font_color

                self.list_items.append(
                    ListItem([state_label, state_type,  state_value,  divider, edit_icon, ender]))

                counter += 1

    def build_states(self):
        self.create_state_list_items()

        self.listview = ListView(
            [0, 54, 572, self.rect[3] - 54], items=self.list_items)
        self.listview.item_selected_color = app_styles.button_color
        self.listview.item_selectable = True
        self.listview.item_row_height = 54

        self.listview_container.add_child(self.listview)

    def update_states(self):
        self.create_state_list_items()
        self.listview.set_data(self.list_items)

    def save_state(self, service_key, state, state_type):
        if service_key not in self.states:
            self.states[service_key] = {}
            self.state_types[service_key] = {}
        self.states[service_key][list(state.keys())[0]] = list(
            state.values())[0]
        self.state_types[service_key][list(state.keys())[0]] = state_type
        self.update_states()

    def update(self, service_key, on_selected_service=True):
        self.current_service_key = service_key
        if on_selected_service:
            if self.current_service_key not in self.states:
                self.states[self.current_service_key] = {}
                self.state_types[self.current_service_key] = {}
        self.update_states()
