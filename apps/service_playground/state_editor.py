from cortic_platform.sdk.ui.basic_widgets import Container, Label
from cortic_platform.sdk.ui.input_widgets import Button, TextField, DropdownList
from utils import *
import app_styles
from cortic_platform.sdk.service_data_types import STATE_DATA_TYPES


class StateEditor(Container):
    def __init__(self, rect, hide_editor, save_state, radius=0, border_color=None, action="Add", subtitle="Enter the details of the new state", state=None):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.action = action
        self.state = state
        self.selected_data_type = None
        self.hide_editor = hide_editor
        self.save_state = save_state
        self.alpha = 1
        self.background_color = app_styles.text_field_color

        self.title = Label([0, 14, self.rect[2], 30],
                           data=self.action + " State")
        self.title.font_size = 18
        self.title.alignment = "center"
        self.title.font_color = app_styles.font_color

        self.subtitle = Label([0, 59, self.rect[2], 20], data=subtitle)
        self.subtitle.font_size = 14
        self.subtitle.alignment = "center"
        self.subtitle.font_color = app_styles.font_color

        self.state_name_label = Label([41, 111, 90, 22], data="State Name")
        self.state_name_label.font_size = 14
        self.state_name_label.alignment = "left"
        self.state_name_label.font_color = app_styles.font_color

        self.state_name_field = TextField([142, 99, 195, 40])
        self.state_name_field.corner_radius = 5
        self.state_name_field.border_color = app_styles.item_color_2
        self.state_name_field.input_font_size = 14
        self.state_name_field.input_font_color = app_styles.font_color
        self.state_name_field.label_font_size = 13
        self.state_name_field.hint_label_font_size = 12
        self.state_name_field.field_background_color = app_styles.item_color_2

        self.state_value_label = Label([41, 223, 90, 22], data="State Value")
        self.state_value_label.font_size = 14
        self.state_value_label.alignment = "left"
        self.state_value_label.font_color = app_styles.font_color

        self.state_value_field = TextField([142, 211, 195, 40])
        self.state_value_field.corner_radius = 5
        self.state_value_field.border_color = app_styles.item_color_2
        self.state_value_field.input_font_size = 14
        self.state_value_field.input_font_color = app_styles.font_color
        self.state_value_field.label_font_size = 13
        self.state_value_field.hint_label_font_size = 12
        self.state_value_field.field_background_color = app_styles.item_color_2

        self.state_value_type_label = Label(
            [41, 167, 90, 22],  data="State Type")
        self.state_value_type_label.font_size = 14
        self.state_value_type_label.alignment = "left"
        self.state_value_type_label.font_color = app_styles.font_color

        self.state_value_type_dropdown = DropdownList(
            [142, 162, 195, 34], items=STATE_DATA_TYPES)
        self.state_value_type_dropdown.background_color = app_styles.item_color_2
        self.state_value_type_dropdown.border_color = app_styles.item_color_2
        self.state_value_type_dropdown.corner_radius = 5
        self.state_value_type_dropdown.on_widget_event = self.on_dropdown_selected
        self.state_value_type_dropdown.label_font_size = 14
        self.state_value_type_dropdown.label_font_color = app_styles.font_color

        self.cancel_button = Button([100, 274, 81, 29])
        self.cancel_button.label = "Cancel"
        self.cancel_button.button_color = app_styles.cancel_button_color
        self.cancel_button.label_font_color = app_styles.font_color
        self.cancel_button.label_font_size = 13
        self.cancel_button.on_widget_event = self.hide_editor

        self.add_state_button = Button([198, 274, 81, 29])
        self.add_state_button.label = "Save"
        self.add_state_button.button_color = app_styles.button_color
        self.add_state_button.label_font_color = app_styles.font_color
        self.add_state_button.label_font_size = 13
        self.add_state_button.on_widget_event = self.save

        self.add_children([self.title, self.subtitle, self.state_name_label, self.state_name_field,
                          self.state_value_label, self.state_value_field, self.state_value_type_label,
                          self.state_value_type_dropdown, self.cancel_button, self.add_state_button])

    def on_dropdown_selected(self, data):
        self.selected_data_type = data

    def save(self, data):
        if self.state_name_field.get_data() != "" and self.state_value_field.get_data() != "":
            state_name = self.state_name_field.get_data()
            state_value = self.state_value_field.get_data()
            state_type = self.selected_data_type
            try:
                state_value = encode_state_value(state_type, state_value)
            except:
                print("Invalid state value")
                return
            state = {state_name: state_value}
            self.save_state(state, state_type)
            self.hide_editor(None)

    def clear_data(self):
        self.state_name_field.clear_data()
        self.state_value_field.clear_data()
        self.state_value_type_dropdown.clear_data()
