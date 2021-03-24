"""This file contains the Game class which is the central element of
our game"""

import signal
import sys
from os import path
import pygame as pg
from src.config.assets import menus_folder
from src.network import Client, Network
from src.Map import Map
from src.Player import Player
from src.utils.network import enqueue_output
from .menu import MenuCharacter, MenuJoin, MenuMain
from src.config.window import RESOLUTION
from src.config.colors import BLACK, WHITE
from src.UI.chat import Chat
from src.ingame_menus import CharacterStatus


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
        # ------PLAYER----- #
        self.player = Player(self.world_map)
        # ------MENUS------ #
        self.main_menu = MenuMain(self)
        self.character_menu = MenuCharacter(self)
        self.join_menu = MenuJoin(self)
        self.current_menu = self.main_menu

        # ----INGAME MENUS---- #
        self.character_status = CharacterStatus(self)

        # ----CHAT---- #
        self.chat = Chat(400, 150, (30, 30), WHITE, 20, self)

        # ----NETWORK---- #
        self.network = Network(self)
        self.client = Client(self)
        self.player_id = dict()
        self.own_id = 10

    def check_events(self):
        "Checks for events in our game"
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if self.menu_running:
                self.current_menu.check_events(event)
            if self.playing:
                if event.type == pg.MOUSEBUTTONDOWN:
                    dest = self.world_map.get_clicked_tile()
                    if self.world_map.is_valid_tile(*dest):
                        self.player.update_path(dest)
                self.chat.event_handler(event)
                if event.type == pg.KEYDOWN:
                    # If we press tab, display the character status menu
                    if event.key == pg.K_TAB:
                        self.character_status.display = True

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
            self.world_map.draw(self.display)
            self.world_map.draw_mini(self.display)
            self.player.move()
            self.player.draw(self.display)
            self.chat.draw(self.display)
            self.character_status.draw()
            self.check_events()
            self.update_screen()
            self.clock.tick(30)
            self.network.server()
