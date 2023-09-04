from cortic_platform.sdk.ui.basic_widgets import Container, Label, HorizontalSeparator
from cortic_platform.sdk.ui.input_widgets import DropdownList
import base64
import ui_layout_tool_styles


class LayoutPreview(Container):
    def __init__(self, rect, widget_tree, background=ui_layout_tool_styles.theme_color, radius=10, border_color=None):
        super().__init__(rect)
        self.use_custom_corner_radius = True
        self.custom_corner_radius = [0, 0, 0, radius]
        self.border_color = border_color
        self.background_color = background
        self.widget_tree = widget_tree
        self.current_file_path = None
        self.widget_group_container_width = rect[2]-14
        self.widget_group_container_height = rect[3]-14-26
        

        self.preview_container = Container([5, 5, rect[2]-14, rect[3]-14])
        self.preview_container.background_color = ui_layout_tool_styles.theme_color_content
        self.preview_container.border_color = ui_layout_tool_styles.theme_color_content
        self.preview_container.corner_radius = radius

        self.title = Label([20, 0, 200, 25], data="Preview")
        self.title.font_size = 12
        self.title.font_color = ui_layout_tool_styles.font_color_dark
        self.title.alignment = "left"

        self.fitting_mode_label = Label([rect[2]-19-105-75, 0, 75, 25], data="Scale Mode")
        self.fitting_mode_label.font_size = 12
        self.fitting_mode_label.font_color = ui_layout_tool_styles.font_color_dark
        self.fitting_mode_label.alignment = "left"

        self.fitting_mode_dropdown = DropdownList(
            [rect[2]-19-105, 2, 85, 21], items=["fit", "full_size"])
        self.fitting_mode_dropdown.background_color = ui_layout_tool_styles.item_color_1
        self.fitting_mode_dropdown.border_color = ui_layout_tool_styles.item_color_1
        self.fitting_mode_dropdown.focused_field_border_color = ui_layout_tool_styles.item_color_1
        self.fitting_mode_dropdown.corner_radius = 5
        self.fitting_mode_dropdown.label_font_size = 12
        self.fitting_mode_dropdown.label_font_color = ui_layout_tool_styles.font_color
        self.fitting_mode_dropdown.on_widget_event = self.change_scale_mode

        self.title_divider = HorizontalSeparator([0, 25, rect[2]-19, 1])
        self.title_divider.line_color = ui_layout_tool_styles.divider_color_2
        self.title_divider.thickness = 1

        self.widget_group_container = Container([0, 26, self.widget_group_container_width, self.widget_group_container_height])
        self.widget_group_container.use_custom_corner_radius = True
        self.widget_group_container.custom_corner_radius = [0, 0, radius, radius]
        self.widget_group_container.background_color = ui_layout_tool_styles.theme_color_content
        self.widget_group_container.border_color = ui_layout_tool_styles.theme_color_content
        self.widget_group_container.border_thickness = 0

        self.preview_container.add_children([self.title, 
                                             self.fitting_mode_label,
                                             self.fitting_mode_dropdown,
                                             self.title_divider, 
                                             self.widget_group_container])

        self.add_child(self.preview_container)

    def change_scale_mode(self, mode):
        if mode == "fit":
            self.widget_group_container.child_fitting_mode = "fit"
        elif mode == "full_size":
            self.widget_group_container.child_fitting_mode = "full_size"
        self.widget_tree.update(self.widget_group_container)
        
    def update_preview(self, widget_group):
        self.widget_group_container.clear_children()
        self.widget_group_container.add_child(widget_group)
        self.widget_tree.update(self.widget_group_container)

    def clear_preview(self):
        self.widget_group_container.clear_children()
        self.widget_tree.update(self.widget_group_container)
