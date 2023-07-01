from cortic_platform.sdk import App
from cortic_platform.sdk.ui.input_widgets import Button
from cortic_platform.sdk.ui.basic_widgets import Container, Image, Label
from cortic_platform.sdk.ui.misc_widgets import CircularLoader
from cortic_platform.sdk.app_events import ExceptionTypes, AppActions
from service_registry import *
import base64
import cv2 
import numpy as np

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class SegmentAnything(App):
    def __init__(self):
        super().__init__()
        self.source_image_numpy = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end = 0
        self.current_box = np.array([])

    def setup(self):
        self.button_selected_color = "#03c24a"
        self.button_unselected_color = "#89b2d3c2"

        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 1
        self.background_container.background = "#2A363B"
        self.background_container.border_color = "#2A363B"
        self.background_container.radius = 10

        self.title_label = Label([0, 30, 1280, 40], data="Open an Image and click on any object you want to segment out", font_size=32, font_color="#ffffff", alignment="center")
        
        self.source_image = Image(
            [100, 160, 500, 375],
            scaling_method="fit",
        )
        self.source_image.capture_mouse_event = True
        self.source_image.on_mouse_event = self.on_mouse_event
        
        self.segmented_image = Image(
            [680, 160, 500, 375],
            scaling_method="fit",
        )

        self.source_image_label = Label([100, 100, 500, 40], data="Source Image", font_size=24, font_color="#ffffff", alignment="center")

        self.browse_source_image_button = Button([100 + (500 - 120)/2, 570, 120, 40], 
                                label="Browse",
                                font_size=20,
                                button_color="#9a9a9a",
                                on_event=self.source_button_callback, 
                                is_file_picker=True)

        self.segmented_image_label = Label([680, 100, 500, 40], data="Segmented Image", font_size=24, font_color="#ffffff", alignment="center")
        
        self.clear_button = Button([(1280-200)/2, 620, 200, 50], 
                                label="Reset",
                                font_size=25,
                                button_color=self.button_selected_color,
                                on_event=self.clear_button_callback)


        self.blank_screen = Container([0, 0, 1280, 720])
        self.blank_screen.alpha = 0.7
        self.blank_screen.background = "#000000"
        self.blank_screen.visible = False
        self.blank_screen.radius = 10
        self.blank_screen.border_color = "#000000"

        self.loader = CircularLoader([(1280 - 60)/2, (720-60)/2, 60, 60], color="#ffffff")
        self.loader.visible = False

        self.background_container.children.append(self.title_label)
        self.background_container.children.append(self.source_image)
        self.background_container.children.append(self.browse_source_image_button)
        self.background_container.children.append(self.source_image_label)
        self.background_container.children.append(self.segmented_image)
        self.background_container.children.append(self.segmented_image_label)
        self.background_container.children.append(self.clear_button)
        self.background_container.children.append(self.blank_screen)
        self.background_container.children.append(self.loader)

        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

    def read_image(self, image_path):
        with open(image_path, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode("ascii")
        return image
    
    def read_image_from_numpy(self, image_numpy):
        _, image = cv2.imencode(".jpeg", image_numpy)
        image = base64.b64encode(image).decode("ascii")
        return image
    
    def source_button_callback(self, data):
        if data != "":
            self.source_image_numpy = cv2.imread(data)
            self.source_image.update_image(self.read_image(data))
            self.scaled_image_width = 375 * self.source_image_numpy.shape[1] / self.source_image_numpy.shape[0]
            self.segmented_image.clear_data()
            self.reset_service_state("mobile_sam")

    def clear_button_callback(self, data):
        self.reset_service_state("mobile_sam")
        self.current_box = np.array([])
        self.source_image.update_image(self.read_image_from_numpy(self.source_image_numpy))
        self.segmented_image.update_image(self.read_image_from_numpy(self.source_image_numpy))
    
    def on_mouse_event(self, event_type, event_data):
        if self.source_image_numpy is not None:
            if event_type == "tap":
                image_x = (event_data["x"] - (500 - self.scaled_image_width)/2) / 375 * self.source_image_numpy.shape[0]
                image_y = event_data["y"] / 375 * self.source_image_numpy.shape[0]
                self.source_image.update_image(self.read_image_from_numpy(self.source_image_numpy))
                self.segment_image(np.array([[int(image_x), int(image_y)]]), np.array([1]), self.current_box)
            elif event_type == "secondary_tap":
                image_x = (event_data["x"] - (500 - self.scaled_image_width)/2) / 375 * self.source_image_numpy.shape[0]
                image_y = event_data["y"] / 375 * self.source_image_numpy.shape[0]
                self.source_image.update_image(self.read_image_from_numpy(self.source_image_numpy))
                self.segment_image(np.array([[int(image_x), int(image_y)]]), np.array([0]), self.current_box)
            elif event_type == "pan_start":
                self.start_x = int((event_data["x"] - (500 - self.scaled_image_width)/2) / 375 * self.source_image_numpy.shape[0])
                self.start_y = int(event_data["y"] / 375 * self.source_image_numpy.shape[0])
                self.source_image.update_image(self.read_image_from_numpy(self.source_image_numpy))
            elif event_type == "pan_update":
                self.end_x = int((event_data["x"] - (500 - self.scaled_image_width)/2) / 375 * self.source_image_numpy.shape[0])
                self.end_y = int(event_data["y"] / 375 * self.source_image_numpy.shape[0])
                drawed_image = cv2.rectangle(self.source_image_numpy.copy(), (self.start_x, self.start_y), (self.end_x, self.end_y), (0, 0, 255), 2)
                self.source_image.update_image(self.read_image_from_numpy(drawed_image))
            elif event_type == "pan_end":
                if self.end_x < self.start_x:
                    temp = self.end_x
                    self.end_x = self.start_x
                    self.start_x = temp
                if self.end_y < self.start_y:
                    temp = self.end_y
                    self.end_y = self.start_y
                    self.start_y = temp
                self.current_box = np.array([int(self.start_x), int(self.start_y), int(self.end_x), int(self.end_y)])
                self.segment_image(np.array([]), np.array([1]), self.current_box)
                self.start_x = 0
                self.start_y = 0
                self.end_x = 0
                self.end = 0

    def segment_image(self, input_points, input_labels, input_box):
        self.blank_screen.visible = True
        self.loader.visible = True
        self.widget_tree.update(self.blank_screen)
        self.widget_tree.update(self.loader)

        result = mobile_sam({"image": self.source_image_numpy, 
                             "input_points": input_points,
                             "input_labels": input_labels,
                             "input_box": input_box,
                             "use_previous_mask": False})

        self.loader.visible = False
        self.blank_screen.visible = False
        self.widget_tree.update(self.loader)
        self.widget_tree.update(self.blank_screen)
        if result:
            if isinstance(result, ExceptionTypes):
                print("Error: ", result)
            else:
                self.segmented_image.update_image(result["masked_image"])

    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass
