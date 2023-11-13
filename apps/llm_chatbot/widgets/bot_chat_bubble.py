import styles
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import math
import base64
from utils import isEnglish
from cortic_platform.sdk.ui.basic_widgets import Container, Label, Image
from cortic_platform.sdk.ui.misc_widgets import CircularLoader

def read_asset_image(filepath):
    with open(filepath, "rb") as image_file:
        image = base64.b64encode(image_file.read()).decode("ascii")
    return image

class BotChatBubble(Container):
    def __init__(self, 
                 rect=[0, 
                       0, 
                       styles.bot_bubble_width, 
                       styles.bot_bubble_height],
                data="",
                loading=False):
        super().__init__(rect)
        self.alpha = 0
        self.data = data
        self.char_per_line = 40
        self.non_english_char_per_line = 20
        self.max_num_line = 5

        self.bot_icon = Image([0, 0, styles.bot_icon_size, styles.bot_icon_size])
        self.bot_icon.alpha = 0
        self.bot_icon.scaling_mode = "fit"
        self.bot_icon.set_data(read_asset_image(os.path.dirname(os.path.realpath(__file__)) + "/../assets/chatbot.png"))

        self.bot_name = Label([styles.bot_icon_size + styles.bot_name_left_margin, 
                               styles.bot_name_top_margin, 
                               styles.bot_name_width, 
                               styles.bot_icon_size], 
                              data="Cortic AI")
        self.bot_name.font_size = styles.bot_name_font_size
        self.bot_name.alignment = "left"
        self.bot_name.font_color = styles.font_color

        self.bot_message = Label([styles.bot_icon_size + styles.bot_message_left_margin,
                                  styles.bot_icon_size + styles.bot_message_top_margin,
                                  styles.bot_message_width,
                                  styles.bot_message_height],
                                 data=data)
        self.bot_message.alpha = 1
        self.bot_message.font_size = styles.bot_message_font_size
        self.bot_message.alignment = "left"
        self.bot_message.font_color = styles.font_color
        self.bot_message.paddings = [styles.bot_message_padding, 
                                     styles.bot_message_padding, 
                                     styles.bot_message_padding, 
                                     styles.bot_message_padding]
        self.bot_message.corner_radius = styles.bot_message_corner_radius
        self.bot_message.background_color = styles.item_color_2
        self.bot_message.border_color = styles.item_color_2
        self.bot_message.selectable = True
        self.bot_message.enable_markdown = False

        self.circular_loader = CircularLoader([self.bot_message.rect[0] + (self.bot_message.rect[2]- styles.bot_message_loader_size)/2, 
                                               self.bot_message.rect[1] + (self.bot_message.rect[3]- styles.bot_message_loader_size)/2, 
                                               styles.bot_message_loader_size,
                                               styles.bot_message_loader_size])
        
        self.circular_loader.visible = loading

        if not loading:
            self.rect[3] = self.bot_message.rect[3] + styles.bot_icon_size + styles.bot_message_top_margin

        self.add_children([self.bot_icon,
                           self.bot_name,
                           self.bot_message,
                           self.circular_loader])
        

    def update_data(self, data):
        num_line = math.ceil(len(data) / self.char_per_line)
        if not isEnglish(data):
            num_line = math.ceil(len(data) / self.non_english_char_per_line)
        # if num_line > self.max_num_line+1:
        #     self.bot_message.scrollable = True
        if num_line > self.max_num_line:
            num_line = self.max_num_line
        self.bot_message.rect[3] = styles.bot_message_height * num_line - (num_line - 1) * styles.bot_message_padding 
        self.bot_message.set_data(data)
        self.circular_loader.visible = False
        self.rect[3] = self.bot_message.rect[3] + styles.bot_icon_size + styles.bot_message_top_margin
        self.root_widget_tree.update(self.circular_loader)
        self.root_widget_tree.update(self.bot_message)
        self.root_widget_tree.update(self)

