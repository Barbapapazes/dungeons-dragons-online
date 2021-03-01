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
from src.utils.network import enqueue_output

from .menu import CharacterMenu, JoinMenu, MainMenu


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

        self.resolution = (1024, 768)
        self.window = pg.display.set_mode(self.resolution)

        # self.display is basically the canvas in which we blit everything
        self.display = pg.Surface(self.resolution)
        self.background = pg.transform.scale(pg.image.load(
            path.join(menus_folder, "background.png")
        ), self.resolution)
        self.display.blit(self.background, (0, 0))

        # ------MENUS------ #
        self.main_menu = MainMenu(self)
        self.character_menu = CharacterMenu(self)
        self.join_menu = JoinMenu(self)
        self.current_menu = self.main_menu

        self.n = Network(self)
        self.c = Client(self)

        # client_ip_port is a set to avoid duplicate. it contains ip string (exemple : {"127.0.0.1:8000","127.0.0.1:8001"})
        self.client_ip_port = set()

        # connections is a dictionnary that contains all the tcpclient subprocess. Keys are the ip:port
        self.connections = {}

        # queue.Queue() is a queue FIFO (First In First Out) with an unlimited size
        self.q = queue.Queue()

        # allow to execute enqueue_output in parallel to read in a NON-BLOCKING way
        self.t = threading.Thread(
            target=enqueue_output, args=(self.n._server.stdout, self.q)
        )
        # the thread will die with the end of the main procuss
        self.t.daemon = True
        # thread is launched
        self.t.start()
        # dic that will contains multiple thread to read tcpclient
        self.ping = {}

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
        self.c.disconnect()
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
            self.update_screen()
            self.check_events()
            self.clock.tick(30)
            self.n.server()
            self.c.send("test\n")
