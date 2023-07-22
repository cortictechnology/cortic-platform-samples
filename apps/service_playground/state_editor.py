from cortic_platform.sdk.ui.basic_widgets import Container, Label
from cortic_platform.sdk.ui.input_widgets import Button, TextField, DropdownMenu
from utils import *
import app_styles
from cortic_platform.sdk.service_data_types import STATE_DATA_TYPES


class StateEditor(Container):
    def __init__(self, rect, hide_editor, save_state, radius=0, border_color=None, action="Add", subtitle="Enter the details of the new state", state=None):
        super().__init__(rect, radius, border_color)
        self.action = action
        self.state = state
        self.selected_data_type = None
        self.hide_editor = hide_editor
        self.save_state = save_state
        self.alpha = 1
        self.background = app_styles.text_field_color

        self.title = Label([0, 14, self.rect[2], 30],
                           font_size=18,
                           alignment="center",
                           font_color=app_styles.font_color,
                           data=self.action + " State")

        self.subtitle = Label([0, 59, self.rect[2], 20],
                              font_size=14,
                              alignment="center",
                              font_color=app_styles.font_color,
                              data=subtitle)

        self.state_name_label = Label([41, 111, 90, 22],
                                      font_size=14,
                                      alignment="left",
                                      font_color=app_styles.font_color,
                                      data="State Name")

        self.state_name_field = TextField([142, 99, 195, 40],
                                          "",
                                          "",
                                          font_size=14,
                                          font_color=app_styles.font_color,
                                          label_font_size=13,
                                          float_label_font_size=12,
                                          fill_color=app_styles.item_color_2)
        self.state_name_field.radius = 5
        self.state_name_field.border_color = app_styles.item_color_2

        self.state_value_label = Label([41, 223, 90, 22],
                                       font_size=14,
                                       alignment="left",
                                       font_color=app_styles.font_color,
                                       data="State Value")

        self.state_value_field = TextField([142, 211, 195, 40],
                                           "",
                                           "",
                                           font_size=14,
                                           font_color=app_styles.font_color,
                                           label_font_size=13,
                                           float_label_font_size=12,
                                           fill_color=app_styles.item_color_2)
        self.state_value_field.radius = 5
        self.state_value_field.border_color = app_styles.item_color_2

        self.state_value_type_label = Label([41, 167, 90, 22],
                                            font_size=14,
                                            alignment="left",
                                            font_color=app_styles.font_color,
                                            data="State Type")

        self.state_value_type_dropdown = DropdownMenu([142, 162, 195, 34],
                                                      font_size=14,
                                                      font_color=app_styles.font_color,
                                                      data_list=STATE_DATA_TYPES)
        self.state_value_type_dropdown.background = app_styles.item_color_2
        self.state_value_type_dropdown.border_color = app_styles.item_color_2
        self.state_value_type_dropdown.radius = 5
        self.state_value_type_dropdown.on_event = self.on_dropdown_selected

        self.cancel_button = Button([100, 274, 81, 29],
                                    label="Cancel",
                                    button_color=app_styles.cancel_button_color,
                                    font_color=app_styles.font_color,
                                    font_size=13,
                                    on_event=self.hide_editor)

        self.add_state_button = Button([198, 274, 81, 29],
                                       label="Save",
                                       button_color=app_styles.button_color,
                                       font_color=app_styles.font_color,
                                       font_size=13,
                                       on_event=self.save)

        self.children += [self.title, self.subtitle, self.state_name_label, self.state_name_field,
                          self.state_value_label, self.state_value_field, self.state_value_type_label,
                          self.state_value_type_dropdown, self.cancel_button, self.add_state_button]

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
