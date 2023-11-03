from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import multiprocessing as mp
import platform
import torch
import queue
import multiprocessing as mp

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


def whisper_worker(input_queue, output_queue, model_size, device, compute_type):
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size,
                         device=device,
                         compute_type=compute_type)
    while True:
        audio_data = input_queue.get()
        if audio_data is None:
            break
        segments, info = model.transcribe(audio_data, beam_size=5)
        segment_texts = []
        text = ""
        for segment in segments:
            segment_texts.append(("[%.2fs -> %.2fs] %s" %
                                  (segment.start, segment.end, segment.text)))
            text += segment.text + " "

        output_queue.put({"detected_language": info.language,
                          "language_probability": info.language_probability,
                          "transcript": text,
                          "segment_texts": segment_texts})


class FasterWhisper(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"audio_chunk": ServiceDataTypes.NumpyArray,
                           "audio_file_path": ServiceDataTypes.String,
                           "model_size": ServiceDataTypes.String}
        self.output_type = {"detected_language": ServiceDataTypes.String,
                            "language_probability": ServiceDataTypes.Float,
                            "transcript": ServiceDataTypes.String,
                            "segment_texts": ServiceDataTypes.List}
        self.model_size = "medium"
        self.valid_model_size = ["small", "medium", "large-v2"]
        self.model = None
        self.device = "cpu"
        self.compute_type = "float16"
        self.whisper_process = None
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        self.context.create_state("blocking", True)

    def activate(self):
        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.compute_type = "int8"
        log("FasterWhisper service activated. Using device: %s" %
            self.device, log_level=LogLevel.Info)

    def process(self, input_data=None):
        audio_chunk = input_data["audio_chunk"]
        audio_file_path = input_data["audio_file_path"]
        if audio_chunk.size == 0 and audio_file_path == "":
            return {"detected_language": "",
                    "language_probability": 0.0,
                    "transcript": "",
                    "segment_texts": []}
        if audio_file_path != "":
            audio_data = audio_file_path
        else:
            audio_data = audio_chunk
        model_size = input_data["model_size"]
        if model_size not in self.valid_model_size:
            log("Invalid model size, using medium model instead",
                log_level=LogLevel.Warning)
            model_size = "medium"
        if self.model is None or self.model_size != model_size:
            self.model_size = model_size
            if self.whisper_process is not None:
                self.whisper_process.terminate()
                self.whisper_process.join()
            self.whisper_process = mp.Process(target=whisper_worker,
                                              args=(self.input_queue,
                                                    self.output_queue,
                                                    self.model_size,
                                                    self.device,
                                                    self.compute_type))
            self.whisper_process.start()
        output = None
        blocking = self.context.get_state("blocking")["blocking"]
        self.input_queue.put(audio_data)
        if blocking:
            while output is None:
                if self._need_deactivate:
                    break
                try:
                    output = self.output_queue.get(True, 0.1)
                except queue.Empty:  # queue here refers to the module, not a class
                    output = None
        else:
            try:
                output = self.output_queue.get(False)
            except queue.Empty:
                pass

        if output is None:
            output = {"detected_language": "",
                      "language_probability": 0.0,
                      "transcript": "",
                      "segment_texts": []}

        return output

    def deactivate(self):
        self.cancel_transcription = False
        if self.whisper_process is not None:
            self.whisper_process.terminate()
            self.whisper_process.join()
        self.whisper_process = None
        self.output_queue.put(None)
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        self.model_size = "medium"
        self.model = None
        self.device = "cpu"
        self.compute_type = "float16"
        log("FasterWhisper service deactivated", log_level=LogLevel.Info)
