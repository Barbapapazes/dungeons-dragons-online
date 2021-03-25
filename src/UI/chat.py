from os import path

from src.config.colors import GREY
from .log import Log
from src.interface.Input import Input
import pygame as pg
from src.config.assets import fonts_folder


class Chat:
    def __init__(self, width, height, position, text_color, font_size, game):
        self.log = Log(width, height, position, text_color, font_size, game)
        self.my_inputbox = Input(
            game, position[0], position[1], width, height, path.join(fonts_folder, 'alegreya.ttf'), font_size, max_length=140)
        self.user_text = ""
        self.text_to_send = ""

    def event_handler(self, event):
        if self.my_inputbox.active and self.my_inputbox.text != "" and event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                self.user_text = self.my_inputbox.text
                self.my_inputbox.flush_text()
                self.log.add_log(self.user_text)

    def draw(self, surface):
        self.log.print_log(surface)
        self.my_inputbox.display_box()
