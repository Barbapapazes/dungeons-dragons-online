"""This file contains the implementation of simple menus"""
from .interface import Button
import pygame as pg


class Menu:
    """The parent menu class"""

    def __init__(self, game):

        self.game = game
        self.displaying = True  # the menu is displayed when displaying is true
        self.menu_background = pg.image.load(
            "src/assets/menus/background.png"
        ).convert_alpha()
        self.clock = pg.time.Clock()

    def display_to_game(self):
        """[summary] This method renders the menu to the game"""
        self.game.window.blit(self.game.display, (0, 0))
        pg.display.update()


class MainMenu(Menu):
    """Defines the main menu with 2 buttons"""

    def __init__(self, game):
        Menu.__init__(self, game)

        self.character_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2,
            "Character Customization",
            "src/fonts/enchanted_land.otf",
            "#000000",
            40,
        )
        self.exit_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 150,
            "Exit Game",
            "src/fonts/enchanted_land.otf",
            "#000000",
            40,
        )

    def check_events(self, event):
        """[summary] This method deals with the user inputs
            on the different buttons of the menu
        Args:
            event ([type]): [description] a pygame event
        """
        if self.character_button.is_clicked(event):
            self.game.current_menu = self.game.character_menu
            self.displaying = False
        if self.exit_button.is_clicked(event):
            self.game.game_quit()

    def display_menu(self):
        """[summary] Displays the menu on our screen"""
        self.displaying = True
        while self.displaying:
            # Checking for events
            self.game.check_events()
            self.game.display.blit(self.menu_background, (0, 0))

            self.character_button.display_button()
            self.character_button.color_on_mouse("#FFFFFF")

            self.exit_button.display_button()
            self.exit_button.color_on_mouse("#FFFFFF")

            self.display_to_game()
            self.clock.tick(30)


class CharacterMenu(Menu):
    """The character customization menu"""

    def __init__(self, game):
        Menu.__init__(self, game)

        self.menu_background = pg.image.load(
            "src/assets/menus/background.png"
        ).convert_alpha()

        self.play_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2,
            "Play",
            "src/fonts/enchanted_land.otf",
            "#000000",
            40,
        )
        self.return_button = Button(
            self.game,
            self.game.resolution[0] // 3,
            self.game.resolution[1] // 2,
            "<",
            "src/fonts/enchanted_land.otf",
            "#000000",
            40,
            "small",
        )
        self.button_list = [self.play_button, self.return_button]

    def check_events(self, event):
        """[summary] This method deals with the user inputs
            on the different buttons of the menu
        Args:
            event ([type]): [description] a pygame event
        """
        if self.play_button.is_clicked(event):
            self.game.menu_running = False
            self.game.playing = True
            self.displaying = False
        if self.return_button.is_clicked(event):
            self.game.current_menu = self.game.main_menu
            self.displaying = False

    def display_menu(self):
        """[summary] Displays the menu on our screen"""
        self.displaying = True
        while self.displaying:
            # Checking for events
            self.game.check_events()
            self.game.display.blit(self.menu_background, (0, 0))

            for button in self.button_list:
                button.display_button()
                button.color_on_mouse("#FFFFFF")

            self.display_to_game()
            self.clock.tick(30)
