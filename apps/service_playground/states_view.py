from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon, VerticalSeparator
from cortic_platform.sdk.ui.input_widgets import ListItem, ListView, Button
from utils import *
import app_styles
import time
from cortic_platform.sdk.service_data_types import STATE_DATA_TYPES


class StatesView(Container):
    def __init__(self, rect, widget_tree, show_state_editor, background=app_styles.theme_color, radius=0, border_color=None):
        super().__init__(rect, radius, border_color)
        self.states = {}
        self.state_types = {}
        self.need_disable_input = False
        self.widget_tree = widget_tree
        self.show_state_editor = show_state_editor
        self.list_items = []
        self.background = background
        self.current_service_key = None

        self.item_backgrounds = [
            app_styles.item_color_1, app_styles.item_color_3]

        self.listview_container = Container(
            [6, 6, 572, 635], radius=10, background=app_styles.theme_color_content,
            border_color=app_styles.theme_color_content)

        self.listview_title_bar = Container(
            [0, 0, 572, 54], background=app_styles.list_selected_color,
            border_color=app_styles.list_selected_color)
        self.listview_title_bar.custom_radius = [10, 10, 0, 0]
        self.listview_title_bar.use_custom_radius = True

        self.listview_title_name = Label([31, 15, 100, 25],
                                         data="State Name",
                                         alignment="center",
                                         font_weight="bold",
                                         font_size=12,
                                         font_color=app_styles.font_color)

        self.listview_title_type = Label([178, 15, 100, 25],
                                         data="State Type",
                                         alignment="center",
                                         font_weight="bold",
                                         font_size=12,
                                         font_color=app_styles.font_color)

        self.listview_title_value = Label([316, 15, 100, 25],
                                          data="State Value",
                                          alignment="center",
                                          font_weight="bold",
                                          font_size=12,
                                          font_color=app_styles.font_color)

        self.listview_title_bar.children += [self.listview_title_name,
                                             self.listview_title_type,
                                             self.listview_title_value]

        self.add_state_button = Button([514, 7, 30, 40],
                                       label="+",
                                       button_color=app_styles.theme_color_highlighted,
                                       font_color=app_styles.font_color_disabled,
                                       font_size=25,
                                       button_radius=0,
                                       on_event=self.on_add_state)

        self.add_state_divider = VerticalSeparator([512, 18, 1, 20],
                                                   color=app_styles.divider_color_3,
                                                   thickness=1)

        self.remove_state_button = Button([544, 7, 30, 40],
                                          label="-",
                                          button_color=app_styles.theme_color_highlighted,
                                          font_color=app_styles.font_color_disabled,
                                          font_size=25,
                                          on_event=self.on_remove_state)

        self.remove_state_divider = VerticalSeparator([542, 18, 1, 20],
                                                      color=app_styles.divider_color_3,
                                                      thickness=1)

        self.listview_container.children += [self.listview_title_bar,
                                             self.add_state_divider,
                                             self.add_state_button, self.remove_state_button,
                                             self.remove_state_divider]

        self.children += [self.listview_container]

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
                state_label = Label([0, 0, 170, 54],
                                    font_size=13,
                                    alignment="left",
                                    font_color=app_styles.font_color,
                                    highlight_color=app_styles.font_color,
                                    paddings=[42, 15, 0, 0],
                                    enable_markdown=False,
                                    data=state)
                state_label.alpha = 1
                state_label.border_color = background
                state_label.background = background

                state_type = Label([0, 0, 113, 54],
                                   font_size=13,
                                   alignment="center",
                                   font_color=app_styles.font_color,
                                   highlight_color=app_styles.font_color,
                                   enable_markdown=False,
                                   data=self.state_types[self.current_service_key][state])
                state_type.alpha = 1
                state_type.border_color = background
                state_type.background = background

                state_value = Label([0, 0, 167, 54],
                                    font_size=13,
                                    alignment="center",
                                    font_color=app_styles.font_color,
                                    highlight_color=app_styles.font_color,
                                    enable_markdown=False,
                                    data=str(self.states[self.current_service_key][state]))
                state_value.alpha = 1
                state_value.border_color = background
                state_value.background = background

                divider = Label([0, 0, 48, 54],
                                font_size=13,
                                alignment="center",
                                font_color=app_styles.font_color,
                                highlight_color=app_styles.font_color,
                                enable_markdown=False,
                                data="")
                divider.alpha = 1
                divider.border_color = background
                divider.background = background

                edit_icon = Icon([0, 0, 40, 54],
                                 size=16,
                                 color=app_styles.font_color,
                                 highlight_color=app_styles.font_color,
                                 data="pencil"
                                 )
                edit_icon.on_event = self.on_edit_state
                edit_icon.clickable = True
                edit_icon.alpha = 1
                edit_icon.border_color = background
                edit_icon.background = background

                ender = Label([0, 0, 30, 54],
                              font_size=13,
                              alignment="center",
                              font_color=app_styles.font_color,
                              highlight_color=app_styles.font_color,
                              enable_markdown=False,
                              data="")
                ender.alpha = 1
                ender.border_color = background
                ender.background = background

                self.list_items.append(
                    ListItem([state_label, state_type,  state_value,  divider, edit_icon, ender]))

                counter += 1

    def build_states(self):
        self.create_state_list_items()

        self.listview = ListView([0, 54, 572, self.rect[3] - 54],
                                 selected_color=app_styles.button_color,
                                 item_radius=0,
                                 selectable=True,
                                 item_padding=0,
                                 can_unselect=True,
                                 data=self.list_items)
        self.listview_container.children.append(self.listview)

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
