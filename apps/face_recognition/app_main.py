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


class FaceRecognition(App):
    def __init__(self):
        super().__init__()
        self.reference_image_numpy = None
        self.query_image_numpy = None

    def setup(self):
        self.button_selected_color = "#03c24a"
        self.button_unselected_color = "#89b2d3c2"

        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 1
        self.background_container.background = "#5F9EA0"
        
        self.reference_image = Image(
            [180, 90, 400, 360],
            scaling_method="fit",
        )
        
        self.query_image = Image(
            [700, 90, 400, 360],
            scaling_method="fit",
        )

        self.reference_image_label = Label([180, 50, 400, 40], data="Reference Image", font_size=24, font_color="#ffffff", alignment="center")

        self.browse_reference_image_button = Button([180 + (400 - 120)/2, 460, 120, 40], 
                                label="Browse",
                                font_size=20,
                                button_color="#9a9a9a",
                                on_event=self.reference_button_callback, 
                                is_file_picker=True)

        self.query_image_label = Label([700, 50, 400, 40], data="Query Image", font_size=24, font_color="#ffffff", alignment="center")

        self.browse_query_image_button = Button([700 + (400 - 120)/2, 460, 120, 40], 
                                label="Browse",
                                font_size=20,
                                button_color="#9a9a9a",
                                on_event=self.query_button_callback,
                                is_file_picker=True)

        self.compare_button = Button([(1280-200)/2, 530, 200, 60], 
                                label="Compare",
                                font_size=25,
                                button_color=self.button_selected_color,
                                on_event=self.compare_button_callback)

        self.loader = CircularLoader([(1280 - 60)/2, (720-60)/2, 60, 60])
        self.loader.visible = False

        self.similarity_label = Label([(1280 - 400)/2, 620, 400, 40], data="Similarity: ", font_size=28, font_color="#ffffff", alignment="center")
        self.similarity_label.visible = False

        self.background_container.children.append(self.reference_image)
        self.background_container.children.append(self.browse_reference_image_button)
        self.background_container.children.append(self.reference_image_label)
        self.background_container.children.append(self.query_image)
        self.background_container.children.append(self.browse_query_image_button)
        self.background_container.children.append(self.query_image_label)
        self.background_container.children.append(self.compare_button)
        self.background_container.children.append(self.loader)
        self.background_container.children.append(self.similarity_label)

        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

    def read_image(self, image_path):
        with open(image_path, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode("ascii")
        return image

    def compare_button_callback(self, data):
        self.loader.visible = True
        self.widget_tree.update(self.loader)
    
        result = face_recognition({"reference_image": self.reference_image_numpy, "query_image": self.query_image_numpy})
        self.loader.visible = False
        self.widget_tree.update(self.loader)
        if result:
            if isinstance(result, ExceptionTypes):
                print("Error: ", result)
            else:
                self.similarity_label.data = "Similarity: " + "{:.1f}".format(result["similarity"] * 100) + "%"
                self.similarity_label.visible = True
                self.widget_tree.update(self.similarity_label)

    def query_button_callback(self, data):
        if data != "":
            self.query_image_numpy = cv2.imread(data)
            self.query_image.update_data("image_data", self.read_image(data))
        if self.similarity_label.visible == True:
            self.similarity_label.visible = False
            self.widget_tree.update(self.similarity_label)

    def reference_button_callback(self, data):
        if data != "":
            self.reference_image_numpy = cv2.imread(data)
            self.reference_image.update_data("image_data", self.read_image(data))
        if self.similarity_label.visible == True:
            self.similarity_label.visible = False
            self.widget_tree.update(self.similarity_label)

    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass
