import app_styles
from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon


class RunButton(Container):
    def __init__(self, rect, background=app_styles.theme_color, radius=0, border_color=None, on_event=None):
        super().__init__(rect)
        self.alpha = 1
        self.corner_radius = radius
        self.border_color = border_color
        self.background_color = background
        self.capture_mouse_event = True
        self.on_widget_event = on_event

        self.icon = Icon([14, 5, 14, 16], data="player_play")
        self.icon.icon_color = app_styles.font_color

        self.label = Label([35, 6, 42, 17], data="Run")
        self.label.font_size = 13
        self.label.alignment = "left"
        self.label.font_color = app_styles.font_color

        self.add_child(self.icon)
        self.add_child(self.label)

    def switch_to_pause(self):
        self.icon.data = "player_pause"
        self.label.data = "Pause"

    def switch_to_play(self):
        self.icon.data = "player_play"
        self.label.data = "Run"
