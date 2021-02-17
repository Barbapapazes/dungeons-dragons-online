"""This file contains the Game class which is the central element of
our game"""
import pygame as pg
from .Menu import CharacterMenu, MainMenu


class Game(object):
    """The game class"""

    def __init__(self):

        self.running = True
        self.playing = False
        self.menu_running = True

        self.resolution = (1920, 1080)
        self.window = pg.display.set_mode(self.resolution)

        # self.display is basically the canvas in which we blit everything
        self.display = pg.Surface(self.resolution)
        self.background = pg.image.load(
            "src/assets/menus/background.png"
        ).convert_alpha()
        self.display.blit(self.background, (0, 0))
        pg.display.set_caption("Donjons & Python")

        # ------MENUS------ #
        self.main_menu = MainMenu(self)
        self.character_menu = CharacterMenu(self)
        # The current menu is the menu we always display
        self.current_menu = self.main_menu

        self.clock = pg.time.Clock()

    def check_events(self):
        "Checks for events in our game"
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.current_menu.displaying = False
                self.running, self.playing = False, False
            if self.menu_running:
                self.current_menu.check_events(event)
            if self.playing:
                # Here we are checking inputs when the game is in the "playing" state
                pass

    def change_player(self):
        """The function to switch the current character in the game"""
        pass

    def game_quit(self):
        """A function to properly quit the game"""
        self.running, self.playing = False, False
        self.current_menu.displaying = False

    def update_screen(self):
        """Updates the whole screen by bliting self.display"""
        self.window.blit(self.display, (0, 0))
        pg.display.update()
        self.window.fill((0, 0, 0))

    def game_loop(self):
        """The loop of the game"""
        while self.playing:
            self.display.fill((0, 0, 0))
            self.update_screen()
            self.check_events()
            self.clock.tick(30)
