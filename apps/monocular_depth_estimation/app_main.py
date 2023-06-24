from cortic_platform.sdk import App
from cortic_platform.sdk.ui.input_widgets import Button
from cortic_platform.sdk.ui.basic_widgets import Container, Image, Label
from cortic_platform.sdk.ui.misc_widgets import CircularLoader
from cortic_platform.sdk.app_events import ExceptionTypes, AppActions
from service_registry import *
import base64
import cv2 


# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class MonocularDepthEstimation(App):
    def __init__(self):
        super().__init__()
        self.source_image_numpy = None

    def setup(self):
        self.button_selected_color = "#03c24a"
        self.button_unselected_color = "#89b2d3c2"

        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 1
        self.background_container.background = "#5F9EA0"
        
        self.source_image = Image(
            [100, 110, 500, 375],
            scaling_method="fit",
        )
        
        self.depth_image = Image(
            [680, 110, 500, 375],
            scaling_method="fit",
        )

        self.source_image_label = Label([100, 50, 500, 40], data="Source Image", font_size=24, font_color="#ffffff", alignment="center")

        self.browse_source_image_button = Button([100 + (500 - 120)/2, 500, 120, 40], 
                                label="Browse",
                                font_size=20,
                                button_color="#9a9a9a",
                                on_event=self.source_button_callback, 
                                is_file_picker=True)

        self.depth_image_label = Label([680, 50, 500, 40], data="Depth Image", font_size=24, font_color="#ffffff", alignment="center")

        self.estimate_depth_button = Button([(1280-300)/2, 590, 300, 60], 
                                label="Estimate Depth",
                                font_size=25,
                                button_color=self.button_selected_color,
                                on_event=self.estimate_depth_button_callback)
        
        self.blank_screen = Container([0, 0, 1280, 720])
        self.blank_screen.alpha = 0.7
        self.blank_screen.background = "#000000"
        self.blank_screen.visible = False

        self.loader = CircularLoader([(1280 - 60)/2, (720-60)/2, 60, 60], color="#ffffff")
        self.loader.visible = False

        self.background_container.children.append(self.source_image)
        self.background_container.children.append(self.browse_source_image_button)
        self.background_container.children.append(self.source_image_label)
        self.background_container.children.append(self.depth_image)
        self.background_container.children.append(self.depth_image_label)
        self.background_container.children.append(self.estimate_depth_button)
        self.background_container.children.append(self.blank_screen)
        self.background_container.children.append(self.loader)

        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

    def read_image(self, image_path):
        with open(image_path, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode("ascii")
        return image
    
    def source_button_callback(self, data):
        if data != "":
            self.source_image_numpy = cv2.imread(data)
            self.source_image.update_data("image_data", self.read_image(data))
        if self.depth_image.data != None:
            self.depth_image.update_data("image_data", None)

    def estimate_depth_button_callback(self, data):
        self.blank_screen.visible = True
        self.loader.visible = True
        self.widget_tree.update(self.blank_screen)
        self.widget_tree.update(self.loader)

        result = glpn_monocular_depth_estimation({"image": self.source_image_numpy})

        self.loader.visible = False
        self.blank_screen.visible = False
        self.widget_tree.update(self.loader)
        self.widget_tree.update(self.blank_screen)
        if result:
            if isinstance(result, ExceptionTypes):
                print("Error: ", result)
            else:
                self.depth_image.update_data("image_data", result["depth_image"])
    
    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass
