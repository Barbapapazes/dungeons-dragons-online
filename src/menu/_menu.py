"""Parent menu for all menu"""
import pygame as pg
from src.config.assets import menus_folder
from src.config.window import RESOLUTION
from os import path


class Menu:
    """The parent menu class"""

    def __init__(self, game):

        self.game = game
        self.displaying = True  # the menu is displayed when displaying is true
        self.menu_background = pg.image.load(
            path.join(menus_folder, "background.png")
        ).convert_alpha()
        self.menu_background = pg.transform.scale(self.menu_background, RESOLUTION)
        

    def display_to_game(self):
        """This method renders the menu to the game"""
        self.game.window.blit(self.game.display, (0, 0))
        pg.display.update()
