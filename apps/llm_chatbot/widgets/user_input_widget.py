import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import styles
from cortic_platform.sdk.ui.basic_widgets import Label, Container
from cortic_platform.sdk.ui.input_widgets import TextField

class UserInputWidget(Container):
    def __init__(self, rect=[0, 0, styles.app_width, styles.user_input_widget_height]):
        super().__init__(rect)
        self.background_color = "#2A2B2D"
        self.border_color = styles.text_field_color
        self.use_custom_corner_radius = True
        self.custom_corner_radius = [0, 0, styles.corner_radius, styles.corner_radius]