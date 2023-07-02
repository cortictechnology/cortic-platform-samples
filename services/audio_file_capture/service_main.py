from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
from pydub import AudioSegment
import numpy as np

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

def pydub_to_np(audio: AudioSegment):
    """
    Converts pydub audio segment into np.float32 of shape [duration_in_seconds*sample_rate, channels],
    where each value is in range [-1.0, 1.0]. 
    Returns tuple (audio_np_array, sample_rate).
    """
    return np.array(audio.get_array_of_samples(), dtype=np.float32).reshape((-1, audio.channels)) / (
            1 << (8 * audio.sample_width - 1)), audio.frame_rate

class AudioFileCapture(Service):
    def __init__(self):
        super().__init__()
        self.output_type = {"audio_frame": ServiceDataTypes.NumpyArray, 
                            "sample_rate": ServiceDataTypes.Int,
                            "num_segment": ServiceDataTypes.Int}
        self.chunk_count = 0

    def activate(self):
        self.audio_file = self.context.get_state("audio_file", "")
        if self.audio_file == "":
            log("No audio file specified", LogLevel.ERROR)
            return
        audio_segment = AudioSegment.from_file(self.audio_file)
        self.audio_np, self.sample_rate = pydub_to_np(audio_segment)
        log("AudioFileCapture: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        if self.audio_file == "":
            return {"audio_frame": np.array([]), "sample_rate": -1, "second": -1}
        segment_duration = self.context.get_state("segment_duration", 1)
        current_audio_frame = self.audio_np[self.chunk_count * self.sample_rate:(self.chunk_count + segment_duration) * self.sample_rate, :]
        self.chunk_count += segment_duration
        if self.chunk_count * self.sample_rate >= self.audio_np.shape[0]:
            self.chunk_count = 0
        return {"audio_frame": current_audio_frame, "sample_rate": self.sample_rate, "num_segment": self.chunk_count}
        
    def deactivate(self):
        self.chunk_count = 0
        self.audio_file == ""
        log("AudioFileCapture: <p style='color:blue'>Deactivated</p>")
