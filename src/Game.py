"""This file contains the Game class which is the central element of
our game"""
import queue
import signal
import subprocess
import threading
import time
from os import path

import pygame as pg

from src.config.assets import menus_folder
from src.config.network import SERVER_PATH
from src.network import Client, Network
from src.utils.network import enqueue_output, get_ip

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
        # The current menu is the menu we always display
        self.current_menu = self.main_menu
        self.join_menu = JoinMenu(self)

        # default port will be increased if already used
        self.my_port = 8000
        tmp_ip = get_ip()
        self.n = Network(self)
        self.c = Client(self)

        # create a subprocess that will execute a new process. list is equivalent to argv[].
        # Pipe (new file-descriptor) are used to allow us to communicate with the process.
        # If we don't precise them the subprocess inherite from the main process and so will use default fd.
        self.serv = subprocess.Popen(
            [SERVER_PATH, str(self.my_port), str(tmp_ip)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # we make the process wait to ensure that the subprocess above has started or ended if an error occured
        time.sleep(0.1)
        # poll check if the process has ended or not. If the process is running the None is returned
        poll = self.serv.poll()
        while poll is not None:
            self.my_port += 1
            self.serv = subprocess.Popen(
                [SERVER_PATH, str(self.my_port), str(tmp_ip)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            time.sleep(0.1)
            poll = self.serv.poll()

        # ip stored in self.my_ip (exemple : 127.0.0.1:8000)
        self.my_ip = str(str(tmp_ip) + ":" + str(self.my_port))
        print(self.my_ip)

        # client_ip_port is a set to avoid duplicate. it contains ip string (exemple : {"127.0.0.1:8000","127.0.0.1:8001"})
        self.client_ip_port = set()

        # connections is a dictionnary that contains all the tcpclient subprocess. Keys are the ip:port
        self.connections = {}

        # queue.Queue() is a queue FIFO (First In First Out) with an unlimied size
        self.q = queue.Queue()

        # allow to execute enqueue_output in parralel to read in a NON-BLOCKING way
        self.t = threading.Thread(
            target=enqueue_output, args=(self.serv.stdout, self.q)
        )
        # the thread will die with the end of the main procus
        self.t.daemon = True
        # thread is launched
        self.t.start()
        # dic that will contains multiple thread to read tcpclient
        self.ping = {}

    def check_events(self):
        "Checks for events in our game"
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.current_menu.displaying = False
                self.running, self.playing = False, False
                self.c.disconnect()
                quit(self)
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
        self.c.disconnect(self)

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
