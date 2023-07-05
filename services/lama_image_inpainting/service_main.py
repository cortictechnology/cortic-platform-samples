from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class LaMaImageInpainting(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {}
        self.output_type = {}

    def activate(self):
        pass

    def process(self, input_data=None):
        pass

    def deactivate(self):
        pass
