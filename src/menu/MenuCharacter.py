"""Character menu"""

from src.menu._menu import Menu
from src.interface import Button
from src.config.assets import fonts_folder, menus_folder
from os import path
from src.config.colors import WHITE
import pygame as pg


class CharacterMenu(Menu):
    """The character customization menu"""

    def __init__(self, game):
        Menu.__init__(self, game)

        self.menu_background = pg.image.load(
            path.join(menus_folder, "background.png")
        ).convert_alpha()

        self.play_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2,
            "Play",
            path.join(fonts_folder, "enchanted_land.otf"),
            WHITE,
            40,
        )
        self.join_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 150,
            "Join",
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

    def check_events(self, event):
        """This method deals with the user inputs
            on the different buttons of the menu
        Args:
            event (Event): a pygame event
        """
        if self.play_button.is_clicked(event):
            self.game.menu_running = False
            self.game.playing = True
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

            self.display_to_game()
            self.game.clock.tick(30)
