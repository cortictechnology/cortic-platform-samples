from cortic_platform.sdk import App
from cortic_platform.sdk.ui.input_widgets import Button, TextField
from cortic_platform.sdk.ui.basic_widgets import Container, Label
from cortic_platform.sdk.ui.misc_widgets import CircularLoader
from cortic_platform.sdk.app_events import ExceptionTypes, AppActions
from service_registry import *
from config import openai_api_key

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class OpenAIChat(App):
    def __init__(self):
        super().__init__()
        self.app_width = 1024
        self.app_height = 600

    def setup(self):
        self.background_container = Container([0, 0, self.app_width, self.app_height])
        self.background_container.alpha = 1
        self.background_container.background = "#23272D"
        self.background_container.border_color = "#23272D"
        self.background_container.radius = 10

        self.title = Label([0, 20, self.app_width, 40], 
                                   data="Hello, I am a Chatbot. How can I help you today?", 
                                   alignment="center", 
                                   font_size=30,
                                   font_color="#ffffff")
        
        self.interaction_container = Container([(self.app_width - 670)/2, 130, 670, 350])
        self.interaction_container.alpha = 1
        self.interaction_container.background = "#23272D"
        self.interaction_container.border_color = "#23272D"

        self.prompt_hint = Label([0, 10, 50, 40],
                                    data="You:",
                                    alignment="left",
                                    font_size=25,
                                    font_color="#ffffff")
        
        self.prompt = TextField([70, 0, 600, 80],
                                "Message",
                                "Type your message here",
                                font_size=23,
                                font_color="#000000",
                                label_font_size=20,
                                float_label_font_size=15,
                                )
        
        
        self.response_hint = Label([0, 120, 50, 40],
                                    data="Bot:",
                                    alignment="left",
                                    font_size=25,
                                    font_color="#ffffff")
        
        self.response = Label([70, 120, 600, 200],
                                data="",
                                alignment="left",
                                font_size=23,
                                font_color="#000000")
        self.response.alpha = 1
        self.response.radius = 10
        self.response.border_color = "#ffffff"
        self.response.background = "#ffffff"
        self.response.scrollable = True

        self.interaction_container.children.append(self.prompt_hint)
        self.interaction_container.children.append(self.prompt)
        self.interaction_container.children.append(self.response_hint)
        self.interaction_container.children.append(self.response)

        self.send_button = Button([(self.app_width-200)/2, self.app_height-60-40, 200, 60], 
                                label="Send Message",
                                font_size=22,
                                button_color="#3c4c85",
                                on_event=self.send_button_callback)

        self.blank_screen = Container([0, 0, self.app_width, self.app_height])
        self.blank_screen.alpha = 0.7
        self.blank_screen.background = "#000000"
        self.blank_screen.visible = False
        self.blank_screen.radius = 10
        self.blank_screen.border_color = "#000000"

        self.loader = CircularLoader([(self.app_width - 60)/2, (self.app_height-60)/2, 60, 60], color="#ffffff")
        self.loader.visible = False

        self.background_container.children.append(self.title)
        self.background_container.children.append(self.interaction_container)
        self.background_container.children.append(self.blank_screen)
        self.background_container.children.append(self.loader)
        self.background_container.children.append(self.send_button)

        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

    def send_button_callback(self, data):
        self.blank_screen.visible = True
        self.loader.visible = True
        self.widget_tree.update(self.loader)
        self.widget_tree.update(self.blank_screen)
    
        response = openai_api_caller({"text_input": {"message": self.prompt.data},
                                      "openai_api_key": openai_api_key})
        
        self.loader.visible = False
        self.blank_screen.visible = False
        self.widget_tree.update(self.loader)
        self.widget_tree.update(self.blank_screen)

        if response:
            if isinstance(response, ExceptionTypes):
                print("Error: ", response)
            else:
                self.response.data = response["response"]
                self.widget_tree.update(self.response)

    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass
