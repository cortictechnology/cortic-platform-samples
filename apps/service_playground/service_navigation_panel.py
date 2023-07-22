from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon
from cortic_platform.sdk.ui.input_widgets import ListItem, ListView
import app_styles


class ServiceNavigationPanel(Container):
    def __init__(self, rect, radius=0, border_color=None, service_list=[], on_event=None):
        super().__init__(rect, radius, border_color)
        self.background = app_styles.theme_color_nvigation
        self.border_color = app_styles.theme_color_nvigation
        self.service_list = service_list

        self.list_items = []
        for service in self.service_list:
            item_icon = Icon([15, 0, 24, 24],
                             size=19,
                             highlight_color=app_styles.font_color,
                             color=app_styles.font_color_disabled, data="tools")
            item = Label([10, 0, 140, 45],
                         font_color=app_styles.font_color_disabled,
                         font_size=14,
                         highlight_color=app_styles.font_color,
                         data=service)
            self.list_items.append(ListItem([item_icon, item]))
        self.listview = ListView([0, 0, rect[2], rect[3]],
                                 selected_color=app_styles.list_selected_color,
                                 item_radius=0,
                                 on_event=on_event,
                                 data=self.list_items)

        self.children.append(self.listview)

    def update(self, service_list):
        self.service_list = service_list
        self.list_items = []
        for service in self.service_list:
            item_icon = Icon([20, 0, 20, 20],
                             size=19,
                             highlight_color=app_styles.font_color,
                             color=app_styles.font_color_disabled, data="tools")
            item = Label([14, 0, 140, 45],
                         font_color=app_styles.font_color_disabled,
                         font_size=14,
                         highlight_color=app_styles.font_color,
                         data=service)
            self.list_items.append(ListItem([item_icon, item]))
        self.listview.set_data(self.list_items)
