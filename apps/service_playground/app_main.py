
from cortic_platform.sdk import App
from cortic_platform.sdk.ui.basic_widgets import Container, Label, HorizontalSeparator, VerticalSeparator
from cortic_platform.sdk.ui.input_widgets import TabBar, Button
from cortic_platform.sdk.ui.misc_widgets import CircularLoader
from cortic_platform.sdk.app_events import ExceptionTypes, AppActions
from cortic_platform.sdk.service_data_types import STATE_DATA_TYPES
import time
import threading
from service_navigation_panel import ServiceNavigationPanel
from run_button import RunButton
from io_view import IOView
from states_view import StatesView
from add_service_dialog import AddServiceDialog
from state_editor import StateEditor
from utils import *
import app_styles

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))


class ServicePlayground(App):
    def __init__(self):
        super().__init__()
        self.stop_scanning = False
        self.selected_view = "io"
        self.selected_service = -1
        self.available_services = {}
        self.selected_service_data = None
        self.selected_service_key = None
        self.processing = False
        self.services_in_playground = []
        self.available_services_list = []
        self.scan_deployed_service_thread = threading.Thread(
            target=self.scan_deployed_service_func, daemon=True)
        self.process_thread = None

    def add_service_to_playground(self, service_key, service):
        if service_key not in self.service_registry:
            self.service_registry[service_key] = {"developer_identifier": service["developer_identifier"],
                                                  "service_name": service["service_name"],
                                                  "major_version": service["major_version"],
                                                  "minor_version":  service["minor_version"]}

        if service["service_name"] not in self.services_in_playground:
            self.services_in_playground.append(service["service_name"])
        self.service_list.update(self.services_in_playground)

    def scan_deployed_service_func(self):
        while not self.stop_scanning:
            self.available_services = {}
            self.available_services_list = []
            available_services = self.get_available_services()
            for service in available_services:
                service_key = service["service_name"].replace(" ", "_") + "_" + \
                    service["developer_identifier"].replace("-", "_") + \
                    "_" + service["major_version"] + \
                    "_" + service["minor_version"]
                self.available_services[service_key] = service
            for service in self.available_services:
                self.available_services_list.append(
                    self.available_services[service]["service_name"])
            updated_available_services = []
            for service in self.available_services_list:
                if service not in self.services_in_playground:
                    updated_available_services.append(service)
            self.add_service_dialog.update_service_list(
                updated_available_services)
            time.sleep(5)

    def add_service(self, data):
        service_to_add = []
        for service in self.add_service_dialog.service_list_view.data:
            if self.add_service_dialog.service_list_view.data[service]:
                service_to_add.append(service)
        for service_name in service_to_add:
            service_key = None
            for service in self.available_services:
                if self.available_services[service]["service_name"] == service_name:
                    service_key = service
                    break
            if service_key is not None:
                self.add_service_to_playground(
                    service_key, self.available_services[service_key])
        self.add_service_dialog.visible = False
        self.widget_tree.update(self.add_service_dialog)
        self.blank_screen.visible = False
        self.widget_tree.update(self.blank_screen)

    def cancel_add_service(self, data):
        self.add_service_dialog.visible = False
        self.widget_tree.update(self.add_service_dialog)
        self.blank_screen.visible = False
        self.widget_tree.update(self.blank_screen)

    def on_select_service(self, selected_service):
        self.blank_screen.visible = True
        self.widget_tree.update(self.blank_screen)
        self.loader.visible = True
        self.widget_tree.update(self.loader)
        if selected_service != self.selected_service:
            if self.processing:
                self.run_button_callback(None)
        self.blank_screen.visible = False
        self.widget_tree.update(self.blank_screen)
        self.loader.visible = False
        self.widget_tree.update(self.loader)
        self.selected_service = selected_service
        self.selected_service_data = None
        if selected_service >= 0 and len(self.available_services) > 0:
            if self.default_message.visible:
                self.default_message.visible = False
                self.widget_tree.update(self.default_message)
            for service in self.available_services:
                if self.available_services[service]["service_name"] == self.services_in_playground[selected_service]:
                    self.selected_service_key = service
                    self.selected_service_data = self.available_services[service]
                    break
            self.update_view(on_selected_service=True)

    def on_select_view(self, view, on_selected_service=False):
        if view == 0:
            self.selected_view = "io"
            if self.selected_service >= 0 and len(self.available_services) > 0:
                if not self.io_view.visible:
                    self.io_view.visible = True
                    self.io_view.update(
                        self.selected_service_data, on_selected_service=on_selected_service)
                    self.widget_tree.update(self.io_view)
                if self.states_view.visible:
                    self.states_view.visible = False
                    self.widget_tree.update(self.states_view)
        else:
            self.selected_view = "states"
            if self.selected_service >= 0 and len(self.available_services) > 0:
                if not self.states_view.visible:
                    self.states_view.visible = True
                    self.states_view.update(
                        self.selected_service_key,
                        on_selected_service=on_selected_service)
                    self.widget_tree.update(self.states_view)
                if self.io_view.visible:
                    self.io_view.visible = False
                    self.widget_tree.update(self.io_view)

    def update_view(self, on_selected_service=True):
        if self.selected_view == "io":
            self.io_view.update(self.selected_service_data)
            self.on_select_view(0, on_selected_service=on_selected_service)
        elif self.selected_view == "states":
            self.states_view.update(
                self.selected_service_key, self.selected_service_data)
            self.on_select_view(1, on_selected_service=on_selected_service)

    def setup_header_bar(self):
        self.header_bar = Container(
            [0, 0, 1280, 70], background=app_styles.theme_color_nvigation, border_color=app_styles.theme_color_nvigation)

        self.content_control_bar = TabBar([215, 10, 1280-220, 50],
                                          texts=["I/O", "States"],
                                          icons=[
                                              "stack_push", "database"],
                                          text_size=20,
                                          icon_size=20,
                                          tab_width=110,
                                          label_color=app_styles.font_color,
                                          unselected_label_color=app_styles.font_color_disabled,
                                          indicator_color=app_styles.indicator_color)
        self.content_control_bar.on_event = self.on_select_view

        self.run_button = RunButton([1162, 20, 85, 30],
                                    background=app_styles.button_color,
                                    border_color=app_styles.button_color,
                                    radius=8,
                                    on_event=self.run_button_callback)

        self.header_bar.children += [self.content_control_bar,
                                     self.run_button]

        self.header_divider = HorizontalSeparator([0, 69, 1280, 1],
                                                  color=app_styles.divider_color,
                                                  thickness=1)

    def on_press_add_service(self, data):
        updated_available_services = []
        for service in self.available_services_list:
            if service not in self.services_in_playground:
                updated_available_services.append(service)
        self.add_service_dialog.update_service_list(
            updated_available_services)
        self.add_service_dialog.service_list_view.clear_data()
        self.add_service_dialog.visible = True
        self.widget_tree.update(self.add_service_dialog)
        self.blank_screen.visible = True
        self.widget_tree.update(self.blank_screen)

    def on_remove_service(self, data):
        if self.selected_service >= 0 and len(self.available_services_list) > 0:
            self.services_in_playground.pop(self.selected_service)
            self.service_list.update(self.services_in_playground)
            time.sleep(0.05)
            if self.selected_service > 0:
                if self.selected_service == len(self.services_in_playground):
                    self.selected_service -= 1
                self.service_list.listview.set_selected_idx(
                    self.selected_service)
            else:
                self.selected_service = -1
                self.selected_service_key = None
                self.selected_service_data = None
                self.io_view.visible = False
                self.widget_tree.update(self.io_view)
                self.states_view.visible = False
                self.widget_tree.update(self.states_view)
                self.default_message.visible = True
                self.widget_tree.update(self.default_message)
                self.service_list.listview.set_selected_idx(
                    self.selected_service)

    def setup_service_navigation_bar(self):
        self.service_navigation_bar = Container(
            [0, 70, 200, 650], background=app_styles.theme_color_nvigation, border_color=app_styles.theme_color_nvigation)

        self.add_service_button = Button([60, 14, 33, 33],
                                         label="+",
                                         button_color=app_styles.theme_color_highlighted,
                                         font_color=app_styles.font_color,
                                         font_size=20,
                                         on_event=self.on_press_add_service)

        self.remove_service_button = Button([101, 14, 33, 33],
                                            label="-",
                                            button_color=app_styles.theme_color_highlighted,
                                            font_color=app_styles.font_color,
                                            font_size=20,
                                            on_event=self.on_remove_service)

        self.service_navigation_bar_divider = HorizontalSeparator([14, 62, 166, 1],
                                                                  color=app_styles.divider_color_2,
                                                                  thickness=1)
        self.service_navigation_bar_divider.opacity = 0.5

        self.service_list = ServiceNavigationPanel(
            [0, 78, 200, 650-78], service_list=self.services_in_playground, on_event=self.on_select_service)

        self.service_navigation_bar.children += [
            self.add_service_button, self.remove_service_button, self.service_navigation_bar_divider, self.service_list]

        self.service_navigation_divider = VerticalSeparator([199, 70, 1, 650],
                                                            color=app_styles.divider_color,
                                                            thickness=1)

    def setup_io_states_view(self):
        self.io_view = IOView([200, 70, 1280-200, 720-70],
                              self.widget_tree,
                              background=app_styles.theme_color,
                              border_color=app_styles.theme_color)
        if self.selected_service == -1 or len(self.available_services) == 0 or self.selected_view != "io":
            self.io_view.visible = False

        self.states_view = StatesView([200, 70, 1280-200, 720-70],
                                      self.widget_tree,
                                      self.show_state_editor,
                                      background=app_styles.theme_color,
                                      border_color=app_styles.theme_color)
        self.states_view.visible = False

    def setup_loading_screen(self):
        self.blank_screen = Container([0, 0, 1280, 720])
        self.blank_screen.alpha = 0.7
        self.blank_screen.background = app_styles.blank_screen_color
        self.blank_screen.visible = False
        self.blank_screen.border_color = app_styles.blank_screen_color

        self.loader = CircularLoader(
            [(1280 - 60)/2, (720-60)/2, 60, 60], color=app_styles.font_color)
        self.loader.visible = False

    def setup_popups(self):
        self.add_service_dialog = AddServiceDialog([451, 157, 378, 406],
                                                   background=app_styles.text_field_color,
                                                   border_color=app_styles.text_field_color,
                                                   radius=10,
                                                   on_add_service=self.add_service,
                                                   on_cancel=self.cancel_add_service,
                                                   service_list=self.available_services_list)
        self.add_service_dialog.visible = False

        self.state_editor = StateEditor([451, 195, 378, 329],
                                        hide_editor=self.hide_state_editor,
                                        save_state=self.save_state,
                                        radius=10,
                                        border_color=app_styles.text_field_color)
        self.state_editor.visible = False

    def show_state_editor(self, action, subtitle, state_name="", state_value="", state_type=0):
        self.state_editor.action = action
        self.state_editor.title.data = action + " State"
        self.state_editor.subtitle.data = subtitle
        self.state_editor.visible = True
        self.widget_tree.update(self.state_editor)
        self.blank_screen.visible = True
        self.widget_tree.update(self.blank_screen)
        time.sleep(0.03)
        self.state_editor.selected_data_type = STATE_DATA_TYPES[state_type]
        self.state_editor.state_name_field.set_data(state_name)
        self.state_editor.state_value_field.set_data(state_value)
        self.state_editor.state_value_type_dropdown.set_selected_item(
            state_type)

    def hide_state_editor(self, data):
        self.state_editor.visible = False
        self.widget_tree.update(self.state_editor)
        self.blank_screen.visible = False
        self.widget_tree.update(self.blank_screen)
        self.state_editor.clear_data()

    def save_state(self, state, state_type):
        self.states_view.save_state(
            self.selected_service_key, state, state_type)

    def setup(self):
        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 1
        self.background_container.background = app_styles.theme_color
        self.background_container.use_custom_radius = True
        self.background_container.custom_radius = [0, 0, 10, 10]

        self.default_message = Label([200, 70, 1280-200, 720-70], data="No service selected",
                                     alignment="center", font_size=20, font_color=app_styles.font_color_disabled)

        self.setup_header_bar()
        self.setup_service_navigation_bar()
        self.setup_io_states_view()
        self.setup_loading_screen()
        self.setup_popups()

        self.background_container.children += [
            self.header_bar, self.header_divider, self.service_navigation_bar,
            self.service_navigation_divider, self.default_message, self.io_view,
            self.states_view, self.blank_screen, self.loader, self.add_service_dialog,
            self.state_editor]

        self.widget_tree.add(self.background_container)
        self.widget_tree.build()

        self.scan_deployed_service_thread.start()

    def get_input_data(self):
        service_input_data, data_ended = self.io_view.get_current_input_data()
        for input_name in service_input_data:
            if service_input_data[input_name] is None:
                return None, data_ended
        for input_name in self.io_view.current_input_widgets:
            if "CvFrame" in input_name:
                service_input_data[input_name] = self.io_view.current_input_data_numpy[input_name]
            else:
                service_input_data[input_name] = encode_input(get_data_type(
                    input_name), self.io_view.current_input_widgets[input_name].data)
        for input_name in service_input_data:
            if service_input_data[input_name] is None:
                return None, data_ended
        return service_input_data, data_ended

    def process_once(self, for_warmup=False):
        if self.selected_service == -1 or len(self.available_services) == 0:
            return None, True
        if for_warmup:
            self.blank_screen.visible = True
            self.loader.visible = True
            self.widget_tree.update(self.blank_screen)
            self.widget_tree.update(self.loader)
        service_output = None
        service_input_data, data_ended = self.get_input_data()
        if service_input_data is None:
            if for_warmup:
                self.loader.visible = False
                self.blank_screen.visible = False
                self.widget_tree.update(self.loader)
                self.widget_tree.update(self.blank_screen)
            return None, True
        else:
            if data_ended and not for_warmup:
                return None, True
        service_function = globals()[self.selected_service_key]
        if service_input_data is not None and service_function:
            input_data = generate_service_input_data(
                self.selected_service_data, service_input_data)
            service_states = {}
            if self.selected_service_key in self.states_view.states:
                service_states = self.states_view.states[self.selected_service_key]
            service_data = service_function(
                input_data, service_states=service_states)
            if service_data:
                service_output = service_data.get_data()
        if for_warmup:
            self.loader.visible = False
            self.blank_screen.visible = False
            self.widget_tree.update(self.loader)
            self.widget_tree.update(self.blank_screen)
        return service_output, False

    def update_output_widgets(self, service_output):
        for output_name in self.io_view.current_output_widgets:
            clean_output_name = output_name[0: output_name.find(
                " (")]
            if get_data_type(output_name) == "CvFrame":
                self.io_view.current_output_widgets[output_name].update_image(
                    service_output[clean_output_name])
            else:
                data_type = get_data_type(output_name)
                data = decode_output(
                    get_data_type(output_name), service_output[clean_output_name])
                if data_type == "NumpyArray":
                    self.io_view.current_output_widgets[output_name].set_data(
                        data)
                else:
                    self.io_view.current_output_widgets[output_name].data = data

    def process_func(self):
        while self.processing:
            service_output, data_ended = self.process_once()
            if service_output:
                self.update_output_widgets(service_output)
            if data_ended:
                self.processing = False
                self.run_button.switch_to_play()
                self.widget_tree.update(self.run_button)
                self.io_view.enable_input()

    def run_button_callback(self, data):
        if not self.processing:
            generated_function_code = '''from cortic_platform.sdk.app_manager import service_handle
@service_handle
def ''' + self.selected_service_key + '''(task_data, device_name='', on_result=None, timeout=None, service_states={}):
    pass
'''
            exec(generated_function_code, globals())
            service_output, data_ended = self.process_once(for_warmup=True)
            if service_output:
                self.update_output_widgets(service_output)
                if not data_ended:
                    self.run_button.switch_to_pause()
                    self.widget_tree.update(self.run_button)
                    self.processing = True
                    self.io_view.disable_input()
                    self.process_thread = threading.Thread(
                        target=self.process_func, daemon=True)
                    self.process_thread.start()
                else:
                    self.processing = False
                    if self.process_thread is not None:
                        self.process_thread.join()
            else:
                self.processing = False
                if self.process_thread is not None:
                    self.process_thread.join()
        else:
            self.run_button.switch_to_play()
            self.widget_tree.update(self.run_button)
            self.processing = False
            self.io_view.enable_input()
            if self.process_thread is not None:
                self.process_thread.join()

    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        self.stop_scanning = True
        pass
