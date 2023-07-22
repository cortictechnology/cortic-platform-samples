from cortic_platform.sdk import App, Pipeline, PipelineNode
from cortic_platform.sdk.ui.basic_widgets import Container, Image
from cortic_platform.sdk.logging import log, LogLevel
from service_registry import *
from utils import read_asset_image

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class OAKDCapture(App):
    def __init__(self):
        super().__init__()

    def setup_ui(self):
        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 0

        self.camera_image = Image(
            [0, 0, 1280, 720],
            data=read_asset_image("background.jpg"),
            scaling_method="fill",
        )

        self.background_container.children.append(self.camera_image)
        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

    def setup_video_pipeline(self):
        self.oakd_pipeline = Pipeline("oakd_pipeline")

        oakd_node = PipelineNode("oakd_capture")

        self.oakd_pipeline.add_node(oakd_node)
        self.oakd_pipeline.set_service_state(
            "oakd_capture", {"action": "capture"})
        self.oakd_pipeline.add_output_port(
            "frame", oakd_node)

        self.oakd_pipeline.start()

    def setup(self):
        self.setup_ui()
        self.setup_video_pipeline()

    def process(self):
        frame = self.oakd_pipeline.get_output_data("frame")
        if frame is not None:
            self.camera_image.update_image(frame["frame"])
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass
