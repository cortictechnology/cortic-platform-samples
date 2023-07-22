import app_styles
from cortic_platform.sdk.ui.basic_widgets import Container, Label, Icon


class RunButton(Container):
    def __init__(self, rect, background=app_styles.theme_color, radius=0, border_color=None, on_event=None):
        super().__init__(rect, radius, border_color)
        self.alpha = 1
        self.clickable = True
        self.background = background
        self.on_event = on_event

        self.icon = Icon([14, 5, 14, 16],
                         color=app_styles.font_color, data="player_play")
        self.label = Label([35, 6, 42, 17],
                           font_size=13,
                           alignment="left",
                           font_color=app_styles.font_color,
                           data="Run")
        self.children.append(self.icon)
        self.children.append(self.label)

    def switch_to_pause(self):
        self.icon.data = "player_pause"
        self.label.data = "Pause"

    def switch_to_play(self):
        self.icon.data = "player_play"
        self.label.data = "Run"
