from src.config.colors import GREY
from .log import Log
from src.interface.Input import Input
import pygame as pg


class Chat:
    def __init__(self, width, height, position, text_color, font_size, game):
        self.log = Log(width, height, position, text_color, font_size, game)
        self.my_inputbox = Input(
            game, position[0], position[1, width, height], pg.font.SysFont("Cascadia code", font_size), max_length=140)
        self.user_text
        self.text_to_send

    def update(self):
        pass

    def event(self):
        pass
