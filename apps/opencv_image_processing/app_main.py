from cortic_platform.sdk import App
from cortic_platform.sdk.ui.input_widgets import Button, DropdownMenu
from cortic_platform.sdk.ui.basic_widgets import Container, Image, Label
from cortic_platform.sdk.ui.misc_widgets import CircularLoader
from cortic_platform.sdk.app_events import ExceptionTypes, AppActions
from service_registry import *
import base64
import cv2 
from utils import supported_functions, function_parameters

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class OpenCVImageProcessing(App):
    def __init__(self):
        super().__init__()
        self.source_image_numpy = None

    def setup(self):
        self.button_selected_color = "#03c24a"
        self.button_unselected_color = "#89b2d3c2"

        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 1
        self.background_container.background = "#22303C"
        self.background_container.border_color = "#22303C"
        self.background_container.radius = 10

        self.select_mode_label = Label([30, 30, 300, 50], data="Select Processing Mode", font_size=25, font_color="#ffffff", alignment="left")
        
        self.mode_menu = DropdownMenu([330, 30, 200, 50],
                                        font_size=22,
                                        font_color="#ffffff",
                                        data_list=supported_functions)
        self.mode_menu.background = "#22303C"
        self.mode_menu.radius = 10
        
        self.source_image = Image(
            [180, 170, 400, 360],
            scaling_method="fit",
        )
        
        self.processed_image = Image(
            [700, 170, 400, 360],
            scaling_method="fit",
        )

        self.source_image_label = Label([180, 130, 400, 40], data="Source Image", font_size=24, font_color="#ffffff", alignment="center")

        self.browse_source_image_button = Button([180 + (400 - 120)/2, 540, 120, 40], 
                                label="Browse",
                                font_size=20,
                                button_color="#9a9a9a",
                                on_event=self.source_button_callback, 
                                is_file_picker=True)

        self.processed_image_label = Label([700, 130, 400, 40], data="Processed Image", font_size=24, font_color="#ffffff", alignment="center")

        self.process_button = Button([(1280-200)/2, 610, 200, 60], 
                                label="Process",
                                font_size=25,
                                button_color=self.button_selected_color,
                                on_event=self.process_button_callback)

        self.blank_screen = Container([0, 0, 1280, 720])
        self.blank_screen.alpha = 0.7
        self.blank_screen.background = "#000000"
        self.blank_screen.visible = False
        self.blank_screen.radius = 10
        self.blank_screen.border_color = "#000000"

        self.loader = CircularLoader([(1280 - 60)/2, (720-60)/2, 60, 60], color="#ffffff")
        self.loader.visible = False

        self.background_container.children.append(self.select_mode_label)
        self.background_container.children.append(self.mode_menu)
        self.background_container.children.append(self.source_image)
        self.background_container.children.append(self.browse_source_image_button)
        self.background_container.children.append(self.source_image_label)
        self.background_container.children.append(self.processed_image)
        self.background_container.children.append(self.processed_image_label)
        self.background_container.children.append(self.process_button)
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
            self.source_image.update_image(self.read_image(data))
            self.processed_image.clear_data()

    def process_button_callback(self, data):
        if self.source_image_numpy is None:
            return
        mode = self.mode_menu.current_value
        self.blank_screen.visible = True
        self.loader.visible = True
        self.widget_tree.update(self.blank_screen)
        self.widget_tree.update(self.loader)

        result = opencv_image_processing({"image_input": {"frame": self.source_image_numpy},
                                          "mode": mode,
                                          "parameters": function_parameters[mode]})

        self.loader.visible = False
        self.blank_screen.visible = False
        self.widget_tree.update(self.loader)
        self.widget_tree.update(self.blank_screen)
        if result:
            if isinstance(result, ExceptionTypes):
                print("Error: ", result)
            else:
                self.processed_image.update_image(result["processed_image"])

    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass
