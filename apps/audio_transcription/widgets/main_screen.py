import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from styles import *
from utils import decode_audio
from numpy_widget import NumpyArrayWidget
from transcription_widget import TranscriptionWidget
from run_button import RunButton
from cortic_platform.sdk.ui.basic_widgets import Container

class MainScreen(Container):
    def __init__(self, on_transcribe=None):
        super().__init__([0, 0, app_width, app_height])
        self.background_color = app_background_color
        self.use_custom_corner_radius = True
        self.custom_corner_radius = [0, 0, corner_radius, corner_radius]
        self.on_transcribe = on_transcribe

        self.data_widget = NumpyArrayWidget(
            [(app_width/2 - data_widget_width)/2,
             (app_height - data_widget_height)/2,
             data_widget_width,
             data_widget_height],
            corner_radius,
            theme_color_content,
            on_event=self.on_selected_file)
        
        self.transcription_widget = TranscriptionWidget(
            [(app_width/2 - data_widget_width)/2 + app_width/2,
             (app_height - data_widget_height)/2,
             data_widget_width,
             data_widget_height],
            corner_radius,
            theme_color_content)
        
        self.run_button = RunButton(
            [(app_width - run_button_width)/2,
             (app_height - run_button_height)/2,
             run_button_width,
             run_button_height],
             on_event=self.on_run_button)

        self.add_children([self.data_widget, self.transcription_widget, self.run_button])

    def on_selected_file(self, data):
        if data != "":
            audio_data = decode_audio(data)
            self.data_widget.set_data(audio_data)
            self.enable_run_button()

    def set_transcription(self, transcription):
        self.transcription_widget.set_data(transcription)

    def on_run_button(self, data):
        if self.on_transcribe is not None:
            self.on_transcribe()

    def enable_run_button(self):
        self.run_button.switch_to_enabled()

    def disable_run_button(self):
        self.run_button.switch_to_disabled()

    def switch_to_loading(self):
        self.run_button.siwtch_to_loading()