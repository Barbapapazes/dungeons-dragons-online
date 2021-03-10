"""This file contains the Game class which is the central element of
our game"""
import queue
import signal
import sys
import threading
from os import path
import pygame as pg
from src.config.assets import menus_folder
from src.network import Client, Network
from src.Map import Map
from src.utils.network import enqueue_output
from .menu import MenuCharacter, MenuJoin, MenuMain
from .Settings import RESOLUTION


class Game:
    """The game class"""

    def __init__(self):

        # create a signal handler that will ignore SIGINT (CTRL + C) signals.
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        pg.init()
        pg.display.set_caption("Donjons & Python")
        pg.mouse.set_cursor(*pg.cursors.tri_left)
        self.clock = pg.time.Clock()

        self.running = True
        self.playing = False
        self.menu_running = True

        self.resolution = RESOLUTION
        self.window = pg.display.set_mode(self.resolution)

        # self.display is basically the canvas in which we blit everything
        self.display = pg.Surface(self.resolution)
        self.background = pg.transform.scale(
            pg.image.load(path.join(menus_folder, "background.png")),
            self.resolution,
        )
        self.display.blit(self.background, (0, 0))

        # -------MAP------- #
        self.world_map = Map("./src/maps/map1/map1.txt")
        # ------MENUS------ #
        self.main_menu = MenuMain(self)
        self.character_menu = MenuCharacter(self)
        self.join_menu = MenuJoin(self)
        self.current_menu = self.main_menu

        self.network = Network(self)
        self.client = Client(self)

    def check_events(self):
        "Checks for events in our game"
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if self.menu_running:
                self.current_menu.check_events(event)
            if self.playing:
                # Here we are checking inputs when the game is in the "playing" state
                pass

    def change_player(self):
        """The function to switch the current character in the game"""
        pass

    def quit(self):
        """A function to properly quit the game"""
        self.running, self.playing = False, False
        self.current_menu.displaying = False
        self.client.disconnect()
        pg.quit()
        sys.exit()

    def update_screen(self):
        """Updates the whole screen by bliting self.display"""
        self.window.blit(self.display, (0, 0))
        pg.display.update()
        self.window.fill((0, 0, 0))

    def game_loop(self):
        """The loop of the game"""
        while self.playing:
            self.display.fill((0, 0, 0))
            self.world_map.draw(self.display, 5, 5)
            self.update_screen()
            self.check_events()
            self.clock.tick(30)
            self.network.server()
            self.client.send("test\n")
