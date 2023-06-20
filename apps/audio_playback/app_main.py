from cortic_platform.sdk import App
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

    def setup(self):
        self.background_container = Container([0, 0, 400, 300])
        self.background_container.background = "#7393B3"

        self.playback_button = Button([(400-150)/2, (300-50)/2, 150, 50], 
                                label="Play Audio",
                                font_size=20,
                                button_color="#03c24a",
                                on_event=self.playback_button_callback)

        self.loader = CircularLoader([(400 - 50)/2, (300-50)/2, 50, 50])
        self.loader.visible = False

        self.background_container.children.append(self.playback_button)
        self.background_container.children.append(self.loader)

        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

    def playback_button_callback(self, data):
        self.loader.visible = True
        self.playback_button.visible = False
        self.widget_tree.update(self.loader)
        self.widget_tree.update(self.playback_button)
        sound = (np.sin(2 * np.pi * np.arange(self.fs * self.duration) * self.freq / self.fs)).astype(np.float32)
        result = audio_playback({"audio_chunk": sound, "sampling_rate": self.fs})
        if result:
            if isinstance(result, ExceptionTypes):
                # print("Error: ", result)
                pass
            else:
                self.loader.visible = False
                self.playback_button.visible = True
                self.widget_tree.update(self.loader)
                self.widget_tree.update(self.playback_button)

    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass
