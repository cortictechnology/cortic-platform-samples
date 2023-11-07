import styles
import os
import math
import base64
from cortic_platform.sdk.ui.basic_widgets import Container, Label, Image

class UserChatBubble(Container):
    def __init__(self, 
                 rect=[0, 
                       0, 
                       styles.user_bubble_width, 
                       styles.user_bubble_height],
                data=""):
        super().__init__(rect)
        self.alpha = 0
        self.data = data
        self.char_per_line = 40
        self.max_num_line = 5

        self.user_name = Label([styles.user_bubble_width - styles.user_name_width, 
                               styles.user_name_top_margin, 
                               styles.user_name_width, 
                               styles.bot_icon_size], 
                              data="User")
        self.user_name.font_size = styles.user_name_font_size
        self.user_name.alignment = "left"
        self.user_name.font_color = styles.font_color

        self.user_message = Label([0,
                                  styles.bot_icon_size + styles.user_message_top_margin,
                                  styles.user_message_width,
                                  styles.user_message_height],
                                 data=data)
        self.user_message.alpha = 1
        self.user_message.font_size = styles.user_message_font_size
        self.user_message.alignment = "left"
        self.user_message.font_color = styles.font_color
        self.user_message.paddings = [styles.user_message_padding, 
                                     styles.user_message_padding, 
                                     styles.user_message_padding, 
                                     styles.user_message_padding]
        self.user_message.corner_radius = styles.user_message_corner_radius
        self.user_message.background_color = styles.text_field_color
        self.user_message.border_color = styles.text_field_color

        num_line = math.ceil(len(data) / self.char_per_line)
        if num_line > self.max_num_line:
            self.user_message.scrollable = True
        if num_line > self.max_num_line:
            num_line = self.max_num_line
        self.user_message.rect[3] = styles.user_message_height * num_line - (num_line - 1) * styles.user_message_padding 

        self.rect[3] = self.user_message.rect[3] + styles.bot_icon_size + styles.user_name_top_margin + styles.user_message_top_margin

        self.add_children([self.user_name, self.user_message])

