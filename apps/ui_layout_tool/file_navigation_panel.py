from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon
from cortic_platform.sdk.ui.input_widgets import ListItem, ListView
import ui_layout_tool_styles


class FileNavigationPanel(Container):
    def __init__(self, rect, radius=0, border_color=None, file_list=[], on_event=None):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.background_color = ui_layout_tool_styles.theme_color_nvigation
        self.border_color = ui_layout_tool_styles.theme_color_nvigation
        self.file_list = file_list

        self.title_label = Label([6, 6, 75, 20], data="Layout Files")
        self.title_label.font_color = ui_layout_tool_styles.font_color_dark
        self.title_label.font_size = 12
        self.title_label.align = "left"

        self.list_items = []
        for file in self.file_list:
            item = Label([15, 0, 180, 30], data=file["file_name"])
            item.font_color = ui_layout_tool_styles.font_color_dark
            item.font_size = 12
            item.highlighted_font_color = ui_layout_tool_styles.font_color

            self.list_items.append(ListItem([item]))

        self.listview = ListView(
            [0, 30, rect[2], rect[3]-30], items=self.list_items)
        self.listview.item_selected_color = ui_layout_tool_styles.list_selected_color
        self.listview.item_radius = 0
        self.listview.item_row_height = 30
        self.listview.on_widget_event = on_event

        self.add_children([self.title_label, self.listview])

    def update(self, file_list, file_paths):
        self.file_list = file_list
        self.list_items = []
        for file in self.file_list:
            item = Label([15, 0, 180, 30], data=file["file_name"])
            item.font_color = ui_layout_tool_styles.font_color_dark
            item.font_size = 12
            item.highlighted_font_color = ui_layout_tool_styles.font_color
            item.tooltip = file_paths[file["file_name_unique"]]
            self.list_items.append(ListItem([item]))
        self.listview.set_data(self.list_items)
