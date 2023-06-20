from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import numpy as np
import sounddevice as sd

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class AudioPlayback(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"audio_chunk": ServiceDataTypes.NumpyArray, "sampling_rate": ServiceDataTypes.Int}
        self.output_type = {"completed": ServiceDataTypes.Boolean}

    def activate(self):
        log("AudioPlayback: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        sd.play(input_data["audio_chunk"], input_data["sampling_rate"], blocking=True)
        return {"completed": True}

    def deactivate(self):
        log("AudioPlayback: <p style='color:blue'>Deactivated</p>")
