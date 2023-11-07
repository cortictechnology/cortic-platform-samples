import styles
from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon
from cortic_platform.sdk.ui.misc_widgets import CircularLoader

class SendButton(Container):
    def __init__(self, 
                 rect=[0, 
                       0, 
                       styles.send_button_size*1.3, 
                       styles.send_button_size*1.3], 
                 background=styles.text_field_color, 
                 border_color=styles.text_field_color, 
                 on_event=None):
        super().__init__(rect)
        self.alpha = 0
        self.corner_radius = 0
        self.background_color = background
        self.border_color = border_color
        self.capture_mouse_event = False
        self.on_widget_event = on_event

        self.icon = Icon([0, 0, self.rect[2], self.rect[3]], data="send")
        self.icon.icon_color = styles.font_color_dark
        self.icon.icon_size = styles.send_button_size

        self.add_child(self.icon)

    def enable_button(self):
        if not self.capture_mouse_event:
            self.capture_mouse_event = True
            self.icon.icon_color = styles.font_color
            self.root_widget_tree.update(self.icon)
            self.root_widget_tree.update(self)

    def disable_button(self):
        if self.capture_mouse_event:
            self.capture_mouse_event = False
            self.icon.icon_color = styles.font_color_dark
            self.root_widget_tree.update(self.icon)
            self.root_widget_tree.update(self)
        
        