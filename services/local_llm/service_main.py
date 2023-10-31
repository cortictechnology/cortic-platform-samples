from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
from llama_cpp import Llama
import os
import json
import threading
import time
import requests
import shutil
from urllib import request
from pathlib import Path
import copy

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

class LocalLLM(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"for_import": ServiceDataTypes.Boolean, 
                           "import_info": ServiceDataTypes.Json, 
                           "for_remove": ServiceDataTypes.Boolean,
                           "model_name": ServiceDataTypes.String,
                           "prompt": ServiceDataTypes.String, 
                           "max_token": ServiceDataTypes.Int, 
                           "stop": ServiceDataTypes.List,
                           "echo": ServiceDataTypes.Boolean}
        self.output_type = {"response": ServiceDataTypes.String}
        self.load_model_records()
        
        self.context.create_state("context_size", 2048)
        self.context.create_state("temp", 0.7)

        self.checking_existing_model = True
        self.currently_loaded_model = None
        self.check_existing_model_thread = threading.Thread(target=self.check_existing_model_func, 
                                                            daemon=True)
        self.check_existing_model_thread.start()
    
        self.llm = None

    def load_model_records(self):
        model_record_file = os.path.dirname(os.path.realpath(__file__)) + "/models/model_records.json"
        model_records = {}
        model_records_copy = {}
        if os.path.exists(model_record_file):
            with open(model_record_file) as f:
                model_records = json.load(f)

        local_model_records = {}
        local_model_record_file = str(Path.home()) + "/Cortic/llm_models/model_records.json"
        if os.path.exists(local_model_record_file):
            with open(local_model_record_file) as f:
                local_model_records = json.load(f)

        for model in local_model_records:
            if model not in model_records:
                model_records[model] = local_model_records[model]

        model_records_copy = copy.deepcopy(model_records)

        for model in model_records:
            model_store_path = str(Path.home()) + "/Cortic/llm_models/" + model + "/"
        if self.context.get_state("models") is None:
            self.context.create_state("models", model_records)
        else:
            self.context.set_state("models", model_records, change_default=True)
        
        # Save model records to local
        if not os.path.exists(str(Path.home()) + "/Cortic/llm_models/"):
            os.makedirs(str(Path.home()) + "/Cortic/llm_models/")
        with open(str(Path.home()) + "/Cortic/llm_models/model_records.json", "w") as f:
            json.dump(model_records_copy, f)
        print("Model records loaded")

    def download_llm_model_func(self, url, model_name):
        try:
            filename = request.urlopen(request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).info().get_filename()
            print("Downloading", model_name, "...")
            r = requests.get(url)
            print("Downloaded, saving...")
            model_store_path = str(Path.home()) + "/Cortic/llm_models/" + model_name + "/"
            if not os.path.exists(model_store_path):
                os.makedirs(model_store_path)
            filepath = model_store_path + filename
            with open(filepath, 'wb') as outfile:
                outfile.write(r.content)
            print("Saved model file for", model_name)
            # Add model to model_records
            model_record_file = os.path.dirname(os.path.realpath(__file__)) + "/models/model_records.json"
            model_records = {} 
            if os.path.exists(model_record_file):
                with open(model_record_file) as f:
                    model_records = json.load(f)
            model_records[model_name] = {"url": url, "filename": filename}
            with open(model_record_file, "w") as f:
                json.dump(model_records, f)
            self.load_model_records()
            return True, ""
        except Exception as e:
            print("Error downloading model:", e)
            return False, str(e)
    
    def copy_model_func(self, file_path, model_name):
        try:
            print("Copying", model_name, "...")
            model_store_path = str(Path.home()) + "/Cortic/llm_models/" + model_name + "/"
            if os.path.exists(model_store_path):
                shutil.rmtree(model_store_path)
            os.makedirs(model_store_path)
            shutil.copy(file_path, model_store_path)
            print("Copied model file for", model_name)
            # Add model to model_records
            model_record_file = os.path.dirname(os.path.realpath(__file__)) + "/models/model_records.json"
            model_records = {} 
            if os.path.exists(model_record_file):
                with open(model_record_file) as f:
                    model_records = json.load(f)
            model_records[model_name] = {"url": "", "filename": os.path.basename(file_path)}
            with open(model_record_file, "w") as f:
                json.dump(model_records, f)
            self.load_model_records()
            return True, ""
        except Exception as e:
            print("Error copying model:", e)
            return False, str(e)

    def check_existing_model_func(self):
        print("Checking existing models...")
        self.checking_existing_model = True
        updated_model_records = {}
        model_records = self.context.get_state("models")["models"]
        model_store_path = str(Path.home()) + "/Cortic/llm_models/"
        for model in model_records:
            filename = model_records[model]["filename"]
            if not os.path.exists(model_store_path + model) or filename == "":
                print(model, " model file not found, downloading...")
                success, message = self.download_llm_model_func(model_records[model]["url"], model)
                if success:
                    updated_model_records[model] = model_records[model]
            else:
                updated_model_records[model] = model_records[model]
        self.context.set_state("models", updated_model_records, change_default=True)
        self.checking_existing_model = False
        print("Model check finished")
        
    def remove_model(self, model_name):
        try:
            print("Removing model...")
            model_records = self.context.get_state("models")["models"]
            model_store_path = str(Path.home()) + "/Cortic/llm_models/"
            filename = model_records[model_name]["filename"]
            model_path = model_store_path + model_name + "/" + filename
            if os.path.exists(model_path):
                os.remove(model_path)
            model_records.pop(model_name)
            self.context.set_state("models", model_records, change_default=True)
            if self.currently_loaded_model == model_name:
                self.currently_loaded_model = None
            model_record_file = os.path.dirname(os.path.realpath(__file__)) + "/models/model_records.json"
            model_records = {} 
            if os.path.exists(model_record_file):
                with open(model_record_file) as f:
                    model_records = json.load(f)
            if model_name in model_records:
                model_records.pop(model_name)
                with open(model_record_file, "w") as f:
                    json.dump(model_records, f)
            local_model_record_file = str(Path.home()) + "/Cortic/llm_models/model_records.json"
            model_records = {}
            if os.path.exists(local_model_record_file):
                with open(local_model_record_file) as f:
                    model_records = json.load(f)
            if model_name in model_records:
                model_records.pop(model_name)
                with open(local_model_record_file, "w") as f:
                    json.dump(model_records, f)
            print("Model removed")
            return True, ""
        except Exception as e:
            print("Error removing model:", e)
            return False, str(e)
    
    def activate(self):
        log("Local LLM service activated", LogLevel.Info)
    
    def load_model(self, model_name):
        model_records = self.context.get_state("models")["models"]
        model_store_path = str(Path.home()) + "/Cortic/llm_models/"
        filename = model_records[model_name]["filename"]
        model_path = model_store_path + model_name + "/" + filename
        context_size = self.context.get_state("context_size")["context_size"]
        self.llm = Llama(model_path=model_path, n_ctx=context_size)
        self.currently_loaded_model = model_name
        print("Loaded model")

    def process(self, input_data=None):
        print("Still checking existing model...")
        response = ""
        while self.checking_existing_model:
            time.sleep(5)
        if input_data["for_import"]:
            model_name = input_data["import_info"]["name"]
            model_url = input_data["import_info"]["url"]
            if "https" in model_url or "http" in model_url or "www" in model_url:
                success, message = self.download_sd_model_func(model_url, model_name)
            else:
                success, message = self.copy_model_func(model_url, model_name)
            if success:
                return {"response": "Model imported successfully"}
            else:
                return {"response": "Error importing model: " + message}
        else:
            if input_data["for_remove"]:
                model_name = input_data["model_name"]
                model_records = self.context.get_state("models")["models"]
                if model_name in model_records:
                    success, message = self.remove_model(model_name)
                if success:
                    return {"response": "Model removed successfully"}
                else:
                    return {"response": "Error removing model: " + message}
            else:
                model_name = input_data["model_name"]
                if self.currently_loaded_model != model_name:
                    self.load_model(model_name)
                prompt = input_data["prompt"]
                max_token = input_data["max_token"]
                stop = input_data["stop"]
                echo = input_data["echo"]
                output = self.llm(prompt, max_tokens=max_token, stop=stop, echo=echo)
                response = output["choices"][0]["text"]
                return {"response": response}

    def deactivate(self):
        log("Local LLM service deactivated", LogLevel.Info)
