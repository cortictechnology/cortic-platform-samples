from cortic_platform.sdk.ui.basic_widgets import Container, Label
from cortic_platform.sdk.ui.input_widgets import Button, CheckboxList
import app_styles


class AddServiceDialog(Container):
    def __init__(self, rect, background=app_styles.theme_color, radius=0, border_color=None, on_add_service=None, on_cancel=None, service_list=[]):
        super().__init__(rect, radius, border_color)
        self.alpha = 1
        self.service_list = service_list
        self.background = background
        self.on_add_service = on_add_service
        self.on_cancel = on_cancel

        self.title = Label([0, 14, rect[2], 29],
                           data="Add Service",
                           alignment="center",
                           font_size=18,
                           font_color=app_styles.font_color)

        self.subtitle = Label([0, 59, rect[2], 20],
                              data="Scanning available services in local network...",
                              alignment="center",
                              font_size=14,
                              font_color=app_styles.font_color)

        self.service_list_container = Container([37, 90, 304, 240],
                                                radius=10,
                                                background=app_styles.theme_color_nvigation,
                                                border_color=app_styles.theme_color_nvigation)
        self.service_list_view = CheckboxList([21, 21, 304-21*2, 240-21*2],
                                              labels=self.service_list,
                                              inactive_color=app_styles.font_color,
                                              active_color=app_styles.button_color,
                                              check_color=app_styles.font_color,
                                              font_size=12,
                                              font_color=app_styles.font_color,
                                              row_height=30,
                                              label_left_padding=10
                                              )
        self.service_list_container.children.append(self.service_list_view)

        self.cancel_button = Button([100, 354, 81, 29],
                                    label="Cancel",
                                    button_color=app_styles.cancel_button_color,
                                    font_color=app_styles.font_color,
                                    font_size=13,
                                    on_event=self.on_cancel)

        self.add_service_button = Button([198, 354, 81, 29],
                                         label="Add",
                                         button_color=app_styles.button_color,
                                         font_color=app_styles.font_color,
                                         font_size=13,
                                         on_event=self.on_add_service)

        self.children += [self.title, self.subtitle,
                          self.service_list_container,
                          self.cancel_button, self.add_service_button]

    def update_service_list(self, service_list):
        self.service_list = service_list
        self.service_list_view.update_data_list(self.service_list)
