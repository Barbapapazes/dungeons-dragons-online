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
from src.Enemy import manage_enemy
from src.utils.network import enqueue_output
from .menu import MenuCharacter, MenuJoin, MenuMain
from src.config.window import RESOLUTION
from src.config.colors import BLACK, WHITE
from src.UI.chat import Chat


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
        self.player = Player(self)
        self.other_player = dict()  # key is the client id, value is a DistantPlayer instance
        # ------ENEMY------ #
        self.enemy_list = []
        # ------MENUS------ #
        self.main_menu = MenuMain(self)
        self.character_menu = MenuCharacter(self)
        self.join_menu = MenuJoin(self)
        self.current_menu = self.main_menu

        # ----CHAT---- #
        self.chat = Chat(400, 150, (30, 30), WHITE, 20, self)

        # ----NETWORK---- #
        self.player_id = dict()
        # Initialized when a party is created (10) or w<hen id is updated from other clients
        self.own_id = -1
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
                if event.type == pg.MOUSEBUTTONDOWN:
                    dest = self.world_map.get_clicked_tile()
                    if self.world_map.is_walkable_tile(*dest):
                        self.player.update_path(dest)
                self.chat.event_handler(event)

                # Here we are checking inputs when the game is in the "playing" state

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
            manage_enemy(self)
            self.player.draw(self.display)
            for o_player in self.other_player.values():
                o_player.draw(self.world_map, self.display)
            self.chat.draw(self.display)
            self.update_screen()
            self.check_events()
            self.clock.tick(30)
            self.network.server()

    def distant_player_move(self, p_id, target):
        """Move the player p_id to the target pos on local game"""
        print(self.other_player)
        exX, exY = self.other_player[int(p_id)].get_current_pos()
        self.world_map.map[exY][exX].wall = False
        self.other_player[int(p_id)].move(*target)
        newX, newY = target
        self.world_map.map[newY][newX].wall = True
