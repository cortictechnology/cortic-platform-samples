from cortic_platform.sdk import App
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.app_events import ExceptionTypes
from service_registry import *
from widgets.main_screen import MainScreen

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class LLMPlayground(App):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.main_screen = MainScreen(on_send_message=self.on_send_message)
        self.widget_tree.add_child(self.main_screen)
        self.widget_tree.build()

        self.main_screen.add_bot_message("Hello, I am Cortic AI. How can I help you?")

    def process(self):
        self.widget_tree.update()

    def on_send_message(self, message):
        self.main_screen.add_user_message(message)
        self.main_screen.add_bot_message("", loading=True)
        chat_task = langchain_chat({"for_import": False,
                                    "import_info": {},
                                    "for_remove": False,
                                    "model_name": "OpenHermes-2.5-Mistral-7B",
                                    "input": message})
        if chat_task and not isinstance(chat_task, ExceptionTypes):
            chat_result = chat_task.get_data(timeout=180)
            self.main_screen.update_bot_message(chat_result["response"])
        self.main_screen.enable_send_button()

    def on_exception(self, exception, exception_data=None):
        log("Exception: {}".format(exception), log_level=LogLevel.Error)

    def teardown(self):
        log("App is tearing down...")