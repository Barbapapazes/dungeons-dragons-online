"""Character menu"""
import os
import signal
from src.menu._menu import Menu
from src.interface import Button, Text, Input
from src.config.assets import fonts_folder, menus_folder
from os import path
from src.config.colors import WHITE
import pygame as pg


class MenuCharacter(Menu):
    """The character customization menu"""

    def __init__(self, game):
        Menu.__init__(self, game)

        self.menu_background = pg.image.load(
            path.join(menus_folder, "background.png")
        ).convert_alpha()

        self.name_text = Text(self.game.display, self.game.resolution[0] // 2, self.game.resolution[1]
                              // 2 - 15, "Enter your character name :", path.join(fonts_folder, "CascadiaCode.ttf"), WHITE, 15, True)

        self.name_input = Input(self.game, self.game.resolution[0] // 2, self.game.resolution[1]
                                // 2 + 25, 350, 40, path.join(fonts_folder, "CascadiaCode.ttf"), 20, 15)

        self.play_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 150,
            "Create game",
            path.join(fonts_folder, "enchanted_land.otf"),
            WHITE,
            40,
        )
        self.join_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 300,
            "Join game",
            path.join(fonts_folder, "enchanted_land.otf"),
            WHITE,
            40,
        )
        self.return_button = Button(
            self.game,
            self.game.resolution[0] // 3,
            self.game.resolution[1] // 2,
            "<",
            path.join(fonts_folder, "enchanted_land.otf"),
            WHITE,
            40,
            "small",
        )
        self.buttons = [
            getattr(self, button)
            for button in dir(self)
            if isinstance(getattr(self, button), Button)
        ]

        self.texts = [
            getattr(self, text)
            for text in dir(self)
            if isinstance(getattr(self, text), Text)
        ]

        self.inputs = [
            getattr(self, input_box)
            for input_box in dir(self)
            if isinstance(getattr(self, input_box), Input)
        ]

    def check_events(self, event):
        """This method deals with the user inputs
            on the different buttons of the menu
        Args:
            event (Event): a pygame event
        """
        self.name_input.handle_events(event)
        if self.play_button.is_clicked(event):
            self.game.menu_running = False
            self.game.playing = True
            # unpause the server
            os.kill(self.game.network._server.pid, signal.SIGUSR2)
            self.displaying = False
        if self.join_button.is_clicked(event):
            self.game.current_menu = self.game.join_menu
            self.displaying = False
        if self.return_button.is_clicked(event):
            self.game.current_menu = self.game.main_menu
            self.displaying = False

    def display_menu(self):
        """Displays the menu on our screen"""
        self.displaying = True
        while self.displaying:
            # Checking for events
            self.game.check_events()
            self.game.display.blit(self.menu_background, (0, 0))

            for button in self.buttons:
                button.display_button()
                button.color_on_mouse(WHITE)

            for input_box in self.inputs:
                input_box.display_box()

            for text in self.texts:
                text.display_text()

            self.display_to_game()
            self.game.clock.tick(30)
