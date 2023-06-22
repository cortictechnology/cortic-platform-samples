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


class ImageClassification(App):
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

    def setup_image_classification_pipeline(self):
        self.image_classification_pipeline = Pipeline("image_classification_pipeline")

        webcam_node = PipelineNode("webcam_capture")
        webcam_node.set_input({"grey_scale": False})
        
        image_classification_node = PipelineNode("image_classification")
        image_classification_node.set_input(
            {"camera_input": webcam_node, 
             "draw_categories": True}
        )
        self.image_classification_pipeline.add_node(webcam_node)
        self.image_classification_pipeline.add_node(image_classification_node)
        self.image_classification_pipeline.add_output_port("classifications", image_classification_node)

        self.image_classification_pipeline.start()

    def setup(self):
        self.setup_ui()
        self.setup_image_classification_pipeline()

    def process(self):
        classifications = self.image_classification_pipeline.get_output_data("classifications")
        if classifications is not None:
            self.webcam_image.update_data("image_data", classifications["annotated_image"])
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        log("Exception happened", log_level=LogLevel.Error)

    def teardown(self):
        pass
