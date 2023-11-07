import styles
from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon
from cortic_platform.sdk.ui.misc_widgets import CircularLoader

class RunButton(Container):
    def __init__(self, 
                 rect=[0, 
                       0, 
                       styles.run_button_width, 
                       styles.run_button_height], 
                 background=styles.button_color, 
                 radius=styles.button_radius, 
                 border_color=styles.button_color, 
                 on_event=None):
        super().__init__(rect)
        self.alpha = 1
        self.corner_radius = radius
        self.background_color = styles.button_disabled_color
        self.border_color = styles.button_disabled_color
        self.capture_mouse_event = False
        self.on_widget_event = on_event

        self.icon = Icon([14, 4.5, 16, 16], data="writing")
        self.icon.icon_color = styles.font_color_dark

        self.label = Label([35, 0, 70, 30], data="Transcribe")
        self.label.font_size = styles.run_button_font_size
        self.label.alignment = "center"
        self.label.font_color = styles.font_color_dark

        self.circular_loader = CircularLoader([(self.rect[2]- styles.run_button_loader_width)/2, 
                                               (self.rect[3]- styles.run_button_loader_height)/2, 
                                               styles.run_button_loader_width,
                                               styles.run_button_loader_height])
        self.circular_loader.color = styles.font_color
        self.circular_loader.visible = False

        self.add_children([self.icon, self.label, self.circular_loader])

    def siwtch_to_loading(self):
        self.capture_mouse_event = False
        self.label.visible = False
        self.circular_loader.visible = True
        self.background_color = styles.button_color
        self.border_color = styles.button_color
        self.label.font_color = styles.font_color
        self.icon.icon_color = styles.font_color
        self.icon.visible = False
        self.root_widget_tree.update(self.label)
        self.root_widget_tree.update(self.circular_loader)
        self.root_widget_tree.update(self.icon)
        self.root_widget_tree.update(self)

    def switch_to_enabled(self):
        self.capture_mouse_event = True
        self.label.visible = True
        self.circular_loader.visible = False
        self.background_color = styles.button_color
        self.border_color = styles.button_color
        self.label.font_color = styles.font_color
        self.icon.icon_color = styles.font_color
        self.icon.visible = True
        self.root_widget_tree.update(self.label)
        self.root_widget_tree.update(self.circular_loader)
        self.root_widget_tree.update(self.icon)
        self.root_widget_tree.update(self)

    def switch_to_disabled(self):
        self.capture_mouse_event = False
        self.label.visible = True
        self.circular_loader.visible = False
        self.background_color = styles.button_disabled_color
        self.border_color = styles.button_disabled_color
        self.label.font_color = styles.font_color_dark
        self.icon.icon_color = styles.font_color_dark
        self.icon.visible = True
        self.root_widget_tree.update(self.label)
        self.root_widget_tree.update(self.circular_loader)
        self.root_widget_tree.update(self.icon)
        self.root_widget_tree.update(self)