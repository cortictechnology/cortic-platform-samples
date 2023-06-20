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

class PoseLandmarks(App):
    def __init__(self):
        super().__init__()

    def setup_ui(self):
        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 0
        
        self.webcam_image = Image(
            [0, 0, 1280, 720],
            data=read_asset_image("background.jpg"),
            scaling_method="fill",
        )

        self.background_container.children.append(self.webcam_image)
        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

    def setup_pose_landmarks_pipeline(self):
        self.pose_landmarks_pipeline = Pipeline("pose_landmarks_pipeline")

        webcam_node = PipelineNode("webcam_capture")
        webcam_node.set_input({"grey_scale": False})
        
        pose_landmarks_node = PipelineNode("pose_landmarks")
        pose_landmarks_node.set_input(
            {"camera_input": webcam_node, 
             "draw_landmarks": True}
        )
        self.pose_landmarks_pipeline.add_node(webcam_node)
        self.pose_landmarks_pipeline.add_node(pose_landmarks_node)
        self.pose_landmarks_pipeline.add_output_port("pose_landmarks", pose_landmarks_node)

        self.pose_landmarks_pipeline.start()

    def setup(self):
        self.setup_ui()
        self.setup_pose_landmarks_pipeline()

    def process(self):
        pose_landmarks = self.pose_landmarks_pipeline.get_output_data("pose_landmarks")
        if pose_landmarks is not None:
            self.webcam_image.update_data("image_data", pose_landmarks["annotated_image"])
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        log("Exception happened", log_level=LogLevel.Error)

    def teardown(self):
        pass
