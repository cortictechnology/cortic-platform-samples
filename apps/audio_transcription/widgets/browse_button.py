from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon
import styles

class BrowseButton(Container):
    def __init__(self,
                 rect=[0,
                       0,
                       styles.data_widget_browse_button_width,
                       styles.data_widget_browse_button_height],
                 background=styles.item_color_2,
                 radius=8,
                 border_color=styles.item_color_2,
                 on_event=None):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.alpha = 1
        self.capture_mouse_event = True
        self.background_color = background
        self.on_widget_event = on_event
        self.for_file_picking = True
        self.file_picking_type = "audio"

        self.icon = Icon([8, 4, 16, 16], data="file_settings")
        self.icon.icon_color = styles.font_color

        self.label = Label([30, 0, 50, 30], data="Browse")
        self.label.font_size = 12
        self.label.alignment = "center"
        self.label.font_color = styles.font_color

        self.add_child(self.icon)
        self.add_child(self.label)
