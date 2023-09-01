from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import openai

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class OpenAIAPICaller(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"text_input": {"message": ServiceDataTypes.String},
                           "openai_api_key": ServiceDataTypes.String}
        self.output_type = {"response": ServiceDataTypes.String}
        self.default_model = "gpt-3.5-turbo"
        self.context.create_state("openai_model", self.default_model)

    def activate(self):
        log("OpenAIAPICaller: <p style='color:blue'>Activated</p>")

    def process(self, input_data=None):
        openai.api_key = input_data["openai_api_key"]
        if openai.api_key is None or openai.api_key == "":
            return {"response": "OpenAI API key not set. Please set it in the service settings."}
        model = self.default_model
        model_state = self.context.get_state("openai_model")
        if model_state is not None:
            model = model_state["openai_model"]
        completion = openai.ChatCompletion.create(model=model, messages=[{"role": "user", "content": input_data["text_input"]["message"]}])
        # print("Response: " + completion.choices[0].message.content)
        return {"response": completion.choices[0].message.content}

    def deactivate(self):
        openai.api_key = None
        log("OpenAIAPICaller: <p style='color:blue'>Deactivated</p>")
