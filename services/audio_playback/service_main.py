from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import numpy as np
import sounddevice as sd
import threading
import time

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class AudioPlayback(Service):
    def __init__(self):
        super().__init__()
        self.audio_data = []
        self.audio_segment = np.array([], dtype=np.float32)
        self.play_audio = False
        self.audio_playing_thread = None
        self.input_type = {"audio_input": {"audio_frame": ServiceDataTypes.NumpyArray,
                                           "sample_rate": ServiceDataTypes.Int,
                                           "num_segment": ServiceDataTypes.Int}}
        self.output_type = {"queued": ServiceDataTypes.Boolean}

    def audio_playing_func(self):
        while self.play_audio:
            if len(self.audio_data) > 0:
                data = self.audio_data.pop(0)
                sd.play(data, samplerate=self.sample_rate, blocking=True)
            else:
                time.sleep(0.01)

    def activate(self):
        self.audio_playing_thread = threading.Thread(target=self.audio_playing_func)
        self.play_audio = True
        self.audio_playing_thread.start()
        log("AudioPlayback: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        self.sample_rate = input_data["audio_input"]["sample_rate"]
        if self.audio_segment.shape[0] < self.sample_rate:
            self.audio_segment = np.append(self.audio_segment, input_data["audio_input"]["audio_frame"])
        else:
            self.audio_data.append(self.audio_segment)
            self.audio_segment = input_data["audio_input"]["audio_frame"]
        return {"queued": True}

    def deactivate(self):
        self.play_audio = False
        self.audio_data = []
        self.audio_playing_thread.join()
        self.audio_playing_thread = None
        log("AudioPlayback: <p style='color:blue'>Deactivated</p>")
