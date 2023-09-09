from cortic_platform.sdk import App
from cortic_platform.sdk.ui.basic_widgets import Container, VerticalSeparator
from cortic_platform.sdk.ui.input_widgets import  Button
from cortic_platform.sdk.app_events import ExceptionTypes, AppActions
from cortic_platform.sdk.logging import log, LogLevel
from service_registry import *
import ui_layout_tool_styles
from file_navigation_panel import FileNavigationPanel
from layout_preview import LayoutPreview
import time
import sys
import os
import inspect
import importlib
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

class  FileChangeHandler(FileSystemEventHandler):
    def  __init__(self, file_change_callback=None):
        self.file_change_callback = file_change_callback

    def  on_modified(self,  event):
        if self.file_change_callback is not None:
            self.file_change_callback(event.src_path)

    def  on_deleted(self,  event):
        if self.file_change_callback is not None:
            self.file_change_callback(event.src_path)

class UILayoutTool(App):
    def __init__(self):
        super().__init__()
        self.app_width = 1280
        self.app_height = 720
        self.layout_files = []
        self.layout_file_paths = {}
        self.selected_file = -1
        self.file_change_handler = None
        self.observer = None

    def load_widget_preview(self, file_index):
        file_name = self.layout_files[file_index]["file_name"]
        module_name = file_name.split(".")[0]
        file_path = self.layout_file_paths[self.layout_files[file_index]["file_name_unique"]]
        file_dir = file_path.split(self.layout_files[file_index]["file_name"])[0]
        files_in_dir = os.listdir(file_dir)
        for file in files_in_dir:
            if ".py" in file:
                module_name = file.split(".")[0]
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        valid_widget_classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if issubclass(obj, Container) and obj.__name__ != "Container":
                        valid_widget_classes.append({"name": name, "obj": obj})
        valid_widgets = {}
        if len(valid_widget_classes) > 0:
            for widget_class in valid_widget_classes:
                try:
                    widget = widget_class["obj"]()
                    if widget.rect[2] == 0 or widget.rect[3] == 0:
                        log("Widget with name " + widget_class["name"] + " has 0 width or height", LogLevel.Error)
                    else:
                        valid_widgets[widget_class["name"]] = widget
                except Exception as e:
                    log("Error creating widget " +  widget_class["name"] + " with error: " + str(e), LogLevel.Error)
                    print(traceback.format_exc())
        else:
            log("No valid Container subclass found in file", LogLevel.Error)
        return valid_widgets
        
    def file_change_callback(self, file_path):
        widget_previews = []
        try:
            widget_previews = self.load_widget_preview(self.selected_file)
        except Exception as e:
            log("Error loading widget group: " + str(e), LogLevel.Error)
            return
        if len(widget_previews) > 0:
            self.layout_preview.update_preview(widget_previews)

    def on_select_file(self, data):
        if len(self.layout_preview.current_avaliable_widget_previews) > 0:
            self.layout_preview.clear_preview()
        if data >=0 and len(self.layout_files) > 0:
            if self.observer is not None:
                self.observer.stop()
                self.observer.join()
                current_file_dir = self.layout_file_paths[self.layout_files[data]["file_name_unique"]].split(self.layout_files[data]["file_name"])[0]
                if current_file_dir in sys.path:
                    sys.path.remove(current_file_dir)
            self.selected_file = data
            self.file_change_handler = FileChangeHandler(file_change_callback=self.file_change_callback)
            self.observer = Observer()
            file_path = self.layout_file_paths[self.layout_files[data]["file_name_unique"]]
            file_dir = file_path.split(self.layout_files[data]["file_name"])[0]
            self.observer.schedule(self.file_change_handler, file_dir)
            self.observer.start()
            sys.path.append(file_dir)
            self.layout_preview.visible = True
            self.widget_tree.update(self.layout_preview)
            try:
                widget_previews = self.load_widget_preview(self.selected_file)
            except Exception as e:
                log("Error loading widget group: " + str(e), LogLevel.Error)
                return
            if len(widget_previews) > 0:
                self.layout_preview.update_preview(widget_previews)
                
    def setup_file_navigation_bar(self):
        self.file_navigation_bar = Container([0, 0, 200, self.app_height])
        self.file_navigation_bar.background_color = ui_layout_tool_styles.theme_color_nvigation
        self.file_navigation_bar.border_thickness = 0
        self.file_navigation_bar.custom_corner_radius = [0, 0, 10, 0]
        self.file_navigation_bar.use_custom_corner_radius = True

        self.file_list = FileNavigationPanel(
            [0, 0, 200, self.app_height], file_list=self.layout_files, on_event=self.on_select_file)
        self.file_list.custom_corner_radius = [0, 0, 10, 0]
        self.file_list.use_custom_corner_radius = True

        self.file_navigation_bar.add_child(self.file_list)

        self.file_navigation_divider = VerticalSeparator([199, 0, 1, self.app_height])
        self.file_navigation_divider.line_color = ui_layout_tool_styles.divider_color
        self.file_navigation_divider.thickness = 1

    def on_press_add_file(self, data):
        split_symbol = "/" # Linux and Mac
        if "\\" in data:
            split_symbol = "\\" # Windows
        file_name = data.split(split_symbol)[-1]
        if ".py" in file_name:
            for file in self.layout_file_paths:
                if self.layout_file_paths[file] == data:
                    log("File already added", LogLevel.Warning)
                    return
            this_file_name = file_name
            if this_file_name in self.layout_file_paths:
                this_file_name = this_file_name.split(".")[0] + "_1.py"
            self.layout_files.append({"file_name_unique": this_file_name, "file_name": file_name})
            self.layout_file_paths[this_file_name] = data
            self.file_list.update(self.layout_files, self.layout_file_paths)
        else:
            log("Only .py files are supported", LogLevel.Warning)
    
    def on_remove_file(self, data):
        if self.selected_file >= 0 and len(self.layout_files) > 0:
            del self.layout_file_paths[self.layout_files[self.selected_file]["file_name_unique"]]
            self.layout_files.pop(self.selected_file)
            self.file_list.update(self.layout_files, self.layout_file_paths)
            time.sleep(0.05)
            if self.selected_file > 0:
                if self.selected_file == len(self.layout_files):
                    self.selected_file -= 1
            else:
                if self.observer is not None:
                    self.observer.stop()
                    self.observer.join()
                self.observer = None
                self.file_change_handler = None
                self.selected_file = -1
                self.layout_preview.visible = False
                self.layout_preview.clear_preview()
                self.widget_tree.update(self.layout_preview)
            self.file_list.listview.set_selected_item(self.selected_file)

    def setup_file_button_container(self):
        self.button_container = Container([0, self.app_height-31, 200, 31])
        self.button_container.background_color = ui_layout_tool_styles.item_color_1
        self.button_container.border_color = ui_layout_tool_styles.item_color_1
        self.button_container.custom_corner_radius = [0, 0, 10, 0]
        self.button_container.use_custom_corner_radius = True

        self.button_container.custom_corner_radius = [0, 0, 10, 0]
        self.button_container.use_custom_corner_radius = True

        self.add_file_button = Button([2, 0, 26, 31])
        self.add_file_button.label = "+"
        self.add_file_button.button_color = ui_layout_tool_styles.item_color_1
        self.add_file_button.label_font_color = ui_layout_tool_styles.font_color_dark
        self.add_file_button.label_font_size = 20
        self.add_file_button.corner_radius = 0
        self.add_file_button.for_file_picking = True
        self.add_file_button.on_widget_event = self.on_press_add_file

        self.add_button_divider = VerticalSeparator([30, 8, 1, 14])
        self.add_button_divider.line_color = ui_layout_tool_styles.divider_color_3
        self.add_button_divider.thickness = 1

        self.remove_file_button = Button([32, 0, 26, 31])
        self.remove_file_button.label = "-"
        self.remove_file_button.button_color = ui_layout_tool_styles.item_color_1
        self.remove_file_button.label_font_color = ui_layout_tool_styles.font_color_dark
        self.remove_file_button.label_font_size = 20
        self.remove_file_button.corner_radius = 0
        self.remove_file_button.on_widget_event = self.on_remove_file

        self.remove_button_divider = VerticalSeparator([60, 8, 1, 14])
        self.remove_button_divider.line_color = ui_layout_tool_styles.divider_color_3
        self.remove_button_divider.thickness = 1

        self.button_container.add_children([
            self.add_file_button,
            self.add_button_divider,
            self.remove_file_button,
            self.remove_button_divider])
        
    def setup_layout_preview(self):
        self.layout_preview = LayoutPreview([200, 0, self.app_width-200, self.app_height],
                                      self.widget_tree,
                                      background=ui_layout_tool_styles.theme_color,
                                      border_color=ui_layout_tool_styles.theme_color)
        if self.selected_file == -1 or len(self.file_list) == 0:
            self.layout_preview.visible = False

    def setup(self):
        self.background_container = Container(
            [0, 0, self.app_width, self.app_height])
        self.background_container.alpha = 1
        self.background_container.background_color = ui_layout_tool_styles.theme_color
        self.background_container.use_custom_corner_radius = True
        self.background_container.custom_corner_radius = [0, 0, 10, 10]

        self.setup_file_navigation_bar()
        self.setup_file_button_container()
        self.setup_layout_preview()

        self.background_container.add_children([
            self.file_navigation_bar,
            self.file_navigation_divider,
            self.button_container,
            self.layout_preview
        ])

        self.widget_tree.add_child(self.background_container)
        self.widget_tree.build()

    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass