from cortic_platform.sdk import App
from cortic_platform.sdk.logging import log, LogLevel
from service_registry import *
from widgets.main_screen import MainScreen
from cortic_platform.sdk.app_events import ExceptionTypes

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class AudioTranscription(App):
    def __init__(self):
        super().__init__()
        self.transcribe_model_size = "medium"

    def setup(self):
        self.main_screen = MainScreen(on_transcribe=self.on_transcribe)
        self.widget_tree.add_child(self.main_screen)
        self.widget_tree.build()

    def process(self):
        self.widget_tree.update()

    def on_transcribe(self):
        self.main_screen.switch_to_loading()
        self.main_screen.set_transcription("")
        audio_data = self.main_screen.data_widget.get_data()
        transcribe_task = faster_whisper_transcription({"audio_chunk": audio_data,
                                                        "audio_file_path": "",
                                                        "model_size": self.transcribe_model_size})
        if transcribe_task is not None and not isinstance(transcribe_task, ExceptionTypes):
            transcribe_result = transcribe_task.get_data()
            self.main_screen.set_transcription(transcribe_result["transcript"])
        self.main_screen.enable_run_button()

    def on_exception(self, exception, exception_data=None):
        log("Exception: {}".format(exception), log_level=LogLevel.Error)

    def teardown(self):
        log("App is tearing down...")
