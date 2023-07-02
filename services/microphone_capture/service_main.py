import pyaudio
import numpy as np
import time
import threading
from collections import deque
from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 48000
CHUNK = 1600

class MicrophoneCaptuerService(Service):
    def __init__(self):
        super().__init__()
        self.audio = None
        self.stream = None
        self.audio_data = None
        self.audio_data_lock = threading.Lock()
        self.output_type = {"audio_frame": ServiceDataTypes.NumpyArray, 
                            "sample_rate": ServiceDataTypes.Int,
                            "num_segment": ServiceDataTypes.Int}

    def callback(self, input_data, frame_count, time_info, flags):
        self.audio_data_lock.acquire()
        self.audio_data = np.fromstring(input_data, dtype="float32")
        self.audio_data_lock.release()
        return input_data, pyaudio.paContinue

    def activate(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            stream_callback=self.callback,
            frames_per_buffer=CHUNK,
        )
        log("MicrophoneCaptuerService: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        self.audio_data_lock.acquire()
        msg = {"audio_frame": np.array([], dtype="float32"),
                "sample_rate": RATE,
                "num_segment": 1}
        if self.audio_data is not None:
            msg["audio_frame"] = self.audio_data
            msg["sample_rate"] = RATE
            msg["num_segment"] = 1
        self.audio_data_lock.release()
        return msg

    def deactivate(self):
        if self.audio is not None:
            self.audio.terminate()
        if self.stream is not None:
            self.stream.close()
        log("MicrophoneCaptuerService: <p style='color:blue'>Deactivated</p>")
