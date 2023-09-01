from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon
from cortic_platform.sdk.ui.input_widgets import ListItem, ListView
import app_styles


class ServiceNavigationPanel(Container):
    def __init__(self, rect, radius=0, border_color=None, service_list=[], on_event=None):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.background_color = app_styles.theme_color_nvigation
        self.border_color = app_styles.theme_color_nvigation
        self.service_list = service_list

        self.list_items = []
        for service in self.service_list:
            item_icon = Icon([20, 0, 20, 20], data="tools")
            item_icon.icon_color = app_styles.font_color_dark
            item_icon.icon_size = 15
            item_icon.highlighted_icon_color = app_styles.font_color

            item = Label([14, 0, 140, 30], data=service)
            item.font_color = app_styles.font_color_dark
            item.font_size = 12
            item.highlighted_font_color = app_styles.font_color

            self.list_items.append(ListItem([item_icon, item]))

        self.listview = ListView(
            [0, 0, rect[2], rect[3]], items=self.list_items)
        self.listview.item_selected_color = app_styles.list_selected_color
        self.listview.item_radius = 0
        self.listview.item_row_height = 30
        self.listview.on_widget_event = on_event

        self.children.append(self.listview)

    def update(self, service_list):
        self.service_list = service_list
        self.list_items = []
        for service in self.service_list:
            item_icon = Icon([20, 0, 20, 20], data="tools")
            item_icon.icon_color = app_styles.font_color_dark
            item_icon.icon_size = 15
            item_icon.highlighted_icon_color = app_styles.font_color

            item = Label([14, 0, 140, 30], data=service)
            item.font_color = app_styles.font_color_dark
            item.font_size = 12
            item.highlighted_font_color = app_styles.font_color
            self.list_items.append(ListItem([item_icon, item]))
        self.listview.set_data(self.list_items)
