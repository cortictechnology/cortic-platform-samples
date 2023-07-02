from cortic_platform.sdk import App, Pipeline, PipelineNode
from cortic_platform.sdk.ui.basic_widgets import Container, Image
from cortic_platform.sdk.ui.input_widgets import Button
from cortic_platform.sdk.ui.misc_widgets import CircularLoader
from cortic_platform.sdk.app_events import ExceptionTypes, AppActions

from service_registry import *
import numpy as np

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class AudioPlayback(App):
    def __init__(self):
        super().__init__()
        self.fs = 44100
        self.freq = 440
        self.duration = 1
        self.audio_source = ""
        self.audio_pipeline_started = False
        self.button_selected_color = "#03c24a"
        self.button_unselected_color = "#89b2d3c2"

    def setup_ui(self):
        self.background_container = Container([0, 0, 400, 300])
        self.background_container.background = "#7393B3"

        self.file_button = Button([(400-300)/2, (300-50)/2, 120, 50], 
                                label="File Source",
                                font_size=10,
                                button_color=self.button_unselected_color,
                                on_event=self.file_button_callback)

        self.microphone_button = Button([(400-300)/2 + 120 + 40, (300-50)/2, 120, 50], 
                                label="Microphone Source",
                                font_size=10,
                                button_color=self.button_unselected_color,
                                on_event=self.microphone_button_callback)

        self.loader = CircularLoader([(400 - 50)/2, (300-50)/2, 50, 50])
        self.loader.visible = False

        self.background_container.children.append(self.microphone_button)
        self.background_container.children.append(self.file_button)
        self.background_container.children.append(self.loader)

        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

    def setup_audio_pipeline(self, source):
        self.audio_pipeline = Pipeline("audio_pipeline")

        if source == "microphone":
            audio_node = PipelineNode("microphone_capture")
        else:
            audio_node = PipelineNode("audio_file_capture")

        audio_playback_node = PipelineNode("audio_playback")
        audio_playback_node.set_input(
            {"audio_input": audio_node}
        )

        self.audio_pipeline.add_node(audio_node)
        self.audio_pipeline.add_node(audio_playback_node)
        
        if source != "microphone":
            self.audio_pipeline.set_service_state(
                "audio_file_capture", {"audio_file": "/Users/michael/development/StarWars60.wav",
                                       "segment_duration": 3,})
        
        self.audio_pipeline.add_output_port("audio_queue_result", audio_playback_node)

        self.audio_pipeline.start()
        self.audio_pipeline_started = True

    def setup(self):
        self.setup_ui()

    def microphone_button_callback(self, data):
        if self.audio_source != "":
            self.audio_pipeline.stop()
            self.audio_source = ""
            self.audio_pipeline_started = False
            self.microphone_button.button_color = self.button_unselected_color
            self.file_button.button_color = self.button_unselected_color
            self.widget_tree.update(self.microphone_button)
            self.widget_tree.update(self.file_button)
        else:
            self.audio_source = "microphone"
            self.microphone_button.button_color = self.button_selected_color
            self.file_button.button_color = self.button_unselected_color
            self.widget_tree.update(self.microphone_button)
            self.widget_tree.update(self.file_button)
            self.setup_audio_pipeline("microphone")
    
    def file_button_callback(self, data):
        if self.audio_source != "":
            self.audio_pipeline.stop()
            self.audio_source = ""
            self.audio_pipeline_started = False
            self.microphone_button.button_color = self.button_unselected_color
            self.file_button.button_color = self.button_unselected_color
            self.widget_tree.update(self.microphone_button)
            self.widget_tree.update(self.file_button)
        else:
            self.audio_source = "file"
            self.microphone_button.button_color = self.button_unselected_color
            self.file_button.button_color = self.button_selected_color
            self.widget_tree.update(self.microphone_button)
            self.widget_tree.update(self.file_button)
            self.setup_audio_pipeline("file")

    def process(self):
        if self.audio_pipeline_started:
            queue_result = self.audio_pipeline.get_output_data("audio_queue_result")
            if queue_result:
                if isinstance(queue_result, ExceptionTypes):
                    print("Error: ", queue_result)
                else:
                    pass
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass
