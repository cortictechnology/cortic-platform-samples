import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import numpy as np
import styles
from cortic_platform.sdk.ui.basic_widgets import Label, Container

class TranscriptionWidget(Container):
    def __init__(self, rect=[0, 0, 450, 500], radius=0, border_color=None, on_event=None):
        super().__init__(rect)
        self.corner_radius = radius
        self.border_color = border_color
        self.background_color = styles.theme_color_content
        self.border_color = styles.theme_color_content
        self.current_data = None

        self.description = Label([(self.rect[2] - styles.input_field_width)/2,
                                  styles.data_widget_subtitle_top_margin,
                                  styles.data_widget_subtitle_width,
                                  styles.data_widget_subtitle_height],
                                 data="Audio Transcription")
        self.description.alignment = "left"
        self.description.font_size = styles.data_widget_subtitle_font_size
        self.description.font_color = styles.font_color

        self.transcription_widget = Label(
            [(self.rect[2] - styles.input_field_width)/2,
             styles.transcription_widget_field_top_margin,
             styles.transcription_widget_field_width,
             styles.transcription_widget_field_height], 
            data="")
        self.transcription_widget.paddings = [10, 10, 20, 20]
        self.transcription_widget.alignment = "left"
        self.transcription_widget.font_size = 12
        self.transcription_widget.font_color = styles.font_color_dark
        self.transcription_widget.alpha = 1
        self.transcription_widget.corner_radius = 10
        self.transcription_widget.border_color = styles.text_field_color
        self.transcription_widget.background_color = styles.text_field_color
        self.transcription_widget.scrollable = True

        self.add_children([self.description, self.transcription_widget])

    def set_data(self, data):
        self.transcription_widget.set_data(data)