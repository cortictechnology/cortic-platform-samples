from cortic_platform.sdk.ui.basic_widgets import Container, Label
from cortic_platform.sdk.ui.input_widgets import Button, CheckboxList
import app_styles


class AddServiceDialog(Container):
    def __init__(self, rect, background=app_styles.theme_color, radius=0, border_color=None, on_add_service=None, on_cancel=None, service_list=[]):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.alpha = 1
        self.service_list = service_list
        self.background_color = background
        self.on_add_service = on_add_service
        self.on_cancel = on_cancel

        self.title = Label([0, 14, rect[2], 29],
                           data="Add Service")
        self.title.alignment = "center"
        self.title.font_size = 18
        self.title.font_color = app_styles.font_color

        self.subtitle = Label([0, 59, rect[2], 20],
                              data="Scanning available services in local network...")
        self.subtitle.alignment = "center"
        self.subtitle.font_size = 14
        self.subtitle.font_color = app_styles.font_color

        self.service_list_container = Container([37, 90, 304, 240])
        self.service_list_container.corner_radius = 10
        self.service_list_container.background_color = app_styles.theme_color_nvigation
        self.service_list_container.border_color = app_styles.theme_color_nvigation

        self.service_list_view = CheckboxList([21, 21, 304-21*2, 240-21*2],
                                              items=self.service_list)
        self.service_list_view.unselected_checkbox_color = app_styles.font_color_dark
        self.service_list_view.selected_checkbox_color = app_styles.button_color
        self.service_list_view.check_color = app_styles.font_color
        self.service_list_view.label_font_size = 12
        self.service_list_view.label_font_color = app_styles.font_color_dark
        self.service_list_view.item_height = 30
        self.service_list_view.label_left_margin = 10

        self.service_list_container.add_child(self.service_list_view)

        self.cancel_button = Button([100, 354, 81, 29])
        self.cancel_button.label = "Cancel"
        self.cancel_button.button_color = app_styles.cancel_button_color
        self.cancel_button.label_font_color = app_styles.font_color
        self.cancel_button.label_font_size = 13
        self.cancel_button.on_widget_event = self.on_cancel

        self.add_service_button = Button([198, 354, 81, 29])
        self.add_service_button.label = "Add"
        self.add_service_button.button_color = app_styles.button_color
        self.add_service_button.label_font_color = app_styles.font_color
        self.add_service_button.label_font_size = 13
        self.add_service_button.on_widget_event = self.on_add_service

        self.add_children([self.title, self.subtitle,
                          self.service_list_container,
                          self.cancel_button, self.add_service_button])

    def update_service_list(self, service_list):
        self.service_list = service_list
        self.service_list_view.update_data_list(self.service_list)
