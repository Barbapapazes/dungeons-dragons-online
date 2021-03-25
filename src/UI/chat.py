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
            game, position[1] + width // 2, position[0] + height + 50, width, 50, path.join(fonts_folder, 'ShareTechMono-Regular.ttf'), font_size, max_length=(width // font_size))
        self.user_text = ""
        self.is_send = False
        self.text_to_send = ""
        self.name = "Default_name"

    def send_chat(self):
        self.text_to_send = "8 "

    def receive_chat(self):
        pass

    def event_handler(self, event):

        if event.type == pg.KEYDOWN:

            if event.key == pg.K_RETURN and self.my_inputbox.get_text() != "":
                self.user_text = self.my_inputbox.get_text()
                if self.user_text[0] == "/":
                    first_word = self.user_text.split()[0]
                    second_word = self.user_text.split()[1]
                    if first_word == "/rename":
                        self.name = second_word

                if self.user_text[0] != "/":
                    self.log.add_log(self.name + " : " + self.user_text)
                self.my_inputbox.flush_text()

        self.my_inputbox.handle_events(event)
        self.log.event(event)

    def draw(self, surface):
        self.log.print_log(surface)
        self.my_inputbox.display_box()

    def commands(self):
        if self.user_text[0] == "/":
            first_word = self.user_text.split()[0]
            second_word = self.user_text.split()[1]
            if first_word == "/rename":
                self.name = second_word
