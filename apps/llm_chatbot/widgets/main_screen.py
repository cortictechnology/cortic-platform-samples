import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from cortic_platform.sdk.ui.basic_widgets import Container
from cortic_platform.sdk.ui.input_widgets import TextField
import styles
from send_button import SendButton
from user_chat_bubble import UserChatBubble
from bot_chat_bubble import BotChatBubble

class MainScreen(Container):
    def __init__(self, on_send_message=None):
        super().__init__([0, 0, styles.app_width, styles.app_height])
        self.on_send_message = on_send_message
        self.background_color = styles.app_background_color
        self.use_custom_corner_radius = True
        self.custom_corner_radius = [0, 0, styles.corner_radius, styles.corner_radius]

        self.chat_history_container = Container([(styles.app_width - styles.chat_history_container_width) / 2, 
                                                 styles.chat_history_container_top_margin, 
                                                 styles.chat_history_container_width, 
                                                 styles.chat_history_container_height])
        self.chat_history_container.background_color = styles.app_background_color
        self.chat_history_container.border_color = styles.app_background_color
        self.chat_history_container.auto_scroll_to_bottom = True

        self.user_input_field = TextField([(styles.app_width - styles.user_input_field_width) / 2, 
                                            styles.app_height - styles.user_input_field_height - styles.user_input_field_bottom_margin, 
                                            styles.user_input_field_width, 
                                            styles.user_input_field_height])
        self.user_input_field.corner_radius = styles.corner_radius
        self.user_input_field.border_color = styles.user_input_field_border_color
        self.user_input_field.label_text = "Send a message..."
        self.user_input_field.hint_text = "Send a message..."
        self.user_input_field.input_font_size = styles.user_input_font_size
        self.user_input_field.input_font_color = styles.font_color_dark
        self.user_input_field.label_font_size = styles.user_input_font_size
        self.user_input_field.expands = True
        self.user_input_field.hint_label_font_size = styles.user_input_font_size
        self.user_input_field.field_background_color = styles.text_field_color
        self.user_input_field.on_widget_event = self.on_user_input

        self.send_button = SendButton([self.user_input_field.rect[0] + self.user_input_field.rect[2] - styles.send_button_container_width-styles.send_button_container_padding, 
                                        self.user_input_field.rect[1] + self.user_input_field.rect[3] - styles.send_button_container_height - styles.send_button_container_padding, 
                                        styles.send_button_container_width, 
                                        styles.send_button_container_height], 
                                        on_event=self.on_send_button_event)
        
        self.add_children([self.chat_history_container,
                           self.user_input_field, 
                           self.send_button])
        
        self.current_message_height = 0
        self.curren_waiting_bot_message = None
    
    def on_user_input(self, data):
        if data != "":
            self.send_button.enable_button()
        else:
            self.send_button.disable_button()

    def on_send_button_event(self, data):
        if self.on_send_message is not None:
            message = self.user_input_field.get_data()
            self.user_input_field.clear_data()
            self.on_send_message(message)
            self.send_button.disable_button()

    def enable_send_button(self):
        self.send_button.enable_button()

    def add_bot_message(self, message, loading=False):
        bot_message = BotChatBubble([styles.bot_bubble_left_margin,
                                     self.current_message_height + styles.bubble_top_margin, 
                                     styles.bot_bubble_width, 
                                     styles.bot_bubble_height], 
                                    data=message,
                                    loading=loading)
        self.chat_history_container.add_child(bot_message)
        if loading:
            self.curren_waiting_bot_message = bot_message
        else:
            self.current_message_height += bot_message.rect[3] + styles.bubble_top_margin
        if self.root_widget_tree:
            self.root_widget_tree.update(self.chat_history_container)

    def update_bot_message(self, message):
        if self.curren_waiting_bot_message:
            self.curren_waiting_bot_message.update_data(message)
            self.current_message_height += self.curren_waiting_bot_message.rect[3] + styles.bubble_top_margin
            self.curren_waiting_bot_message = None
            if self.root_widget_tree:
                self.root_widget_tree.update(self.chat_history_container)

    def add_user_message(self, message):
        user_message = UserChatBubble([self.chat_history_container.rect[2] - styles.user_bubble_right_margin - styles.user_bubble_width, 
                                       self.current_message_height + styles.bubble_top_margin, 
                                       styles.user_bubble_width, 
                                       styles.user_bubble_height], 
                                      message)
        self.chat_history_container.add_child(user_message)
        self.current_message_height += user_message.rect[3] + styles.bubble_top_margin
        if self.root_widget_tree:
            self.root_widget_tree.update(self.chat_history_container)
