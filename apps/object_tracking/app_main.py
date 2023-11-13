from cortic_platform.sdk import App, Pipeline, PipelineNode
from cortic_platform.sdk.ui.basic_widgets import Container, Label, Image
from cortic_platform.sdk.ui.visualization_utils import encode_jpeg, draw_object_detection
from cortic_platform.sdk.logging import log, LogLevel
from service_registry import *

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

class ObjectTracking(App):
    def __init__(self):
        super().__init__()
        self.use_yolov8 = True

    def setup(self):
        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 0
        
        self.webcam_image = Image(
            [0, 0, 1280, 720]
        )
        self.webcam_image.scaling_mode = "fill"

        self.background_container.add_child(self.webcam_image)
        self.widget_tree.add_child(self.background_container)
        self.widget_tree.build()
    
        self.setup_tracking_pipeline()

    def setup_tracking_pipeline(self):
        self.tracking_pipeline = Pipeline("tracking_pipeline")

        webcam_node = PipelineNode("webcam_capture", device_name="M2 Pro Mac Mini")
        byte_tracker_node = PipelineNode("byte_tracker", device_name="M2 Pro Mac Mini")
        self.tracking_pipeline.add_node(webcam_node)
        
        object_detection_node = PipelineNode("object_detection", device_name="M2 Pro Mac Mini")
        object_detection_node.set_input(
            {"camera_input": webcam_node}
        )
        byte_tracker_node.set_input(
            {"detection_result": object_detection_node}
        )
        self.tracking_pipeline.add_node(object_detection_node)

        self.tracking_pipeline.add_node(byte_tracker_node)
        self.tracking_pipeline.add_output_port("detections", byte_tracker_node)

        self.tracking_pipeline.start()

    def process(self):
        detections = self.tracking_pipeline.get_output_data("detections")
        if detections is not None:
            annotated_image = encode_jpeg(draw_object_detection(detections["frame"], detections["detections"]))
            self.webcam_image.set_data(annotated_image)
        self.widget_tree.update()
    
    def on_exception(self, exception, exception_data=None):
        log("Exception happened", log_level=LogLevel.Error)

    def teardown(self):
        pass
