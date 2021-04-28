"""Join menu"""
import queue
import subprocess
import threading
import time
import os
import signal
from os import path


import pygame as pg
from src.config.assets import fonts_folder, menus_folder
from src.config.colors import WHITE
from src.interface import Button, Input
from src.menu._menu import Menu

from src.utils.network import enqueue_output


class MenuJoin(Menu):
    """Menu to join a game"""

    def __init__(self, game):
        Menu.__init__(self, game)

        self.menu_background = pg.image.load(
            path.join(menus_folder, "background.png")
        ).convert_alpha()

        self.ip_input = Input(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2,
            200,
            50,
            path.join(fonts_folder, "enchanted_land.otf"),
            32,
            20,
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

        self.join_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 150,
            "Join",
            path.join(fonts_folder, "enchanted_land.otf"),
            WHITE,
            40,
        )

        self.buttons = [
            getattr(self, button)
            for button in dir(self)
            if isinstance(getattr(self, button), Button)
        ]

        self.inputs = [
            getattr(self, input)
            for input in dir(self)
            if isinstance(getattr(self, input), Input)
        ]

    def check_events(self, event):
        """This method deals with the user inputs
            on the different buttons of the menu
        Args:
            event (Event): a pygame event
        """
        self.ip_input.handle_events(event)
        if self.return_button.is_clicked(event):
            self.game.current_menu = self.game.character_menu
            self.displaying = False
        if self.join_button.is_clicked(event):
            client_ip = self.ip_input.get_text()
            tmp = client_ip.split(":")
            if len(tmp) != 2:
                return
            # initialize a connection to ip contained in sys.argv[2]
            tmp_proc = subprocess.Popen(
                ["./src/tcpclient", tmp[0], tmp[1]],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            time.sleep(0.11)
            poll = tmp_proc.poll()
            if poll is not None:
                return
            self.displaying = False
            self.game.menu_running = False
            # unpause the server
            os.kill(self.game.network._server.pid, signal.SIGUSR2)
            self.game.network.client_ip_port.add(client_ip)
            # split the ip:port to obtains ip and port
            tmp = client_ip.split(":")
            # initialize a connection to ip contained in sys.argv[2]
            self.game.network.connections[client_ip] = tmp_proc
            # encode in binary a message that contains : first + client ip:port
            msg = str(str(self.game.own_id) + " 0 " + str(self.game.network.ip)
                      + ":" + str(self.game.network.port))
            self.game.network.send_message(msg, client_ip)

            # queue.Queue() is a queue FIFO (First In First Out) with an unlimied size
            tmp_queue = queue.Queue()
            tmp_thread = threading.Thread(
                target=enqueue_output,
                args=(
                    self.game.network.connections[client_ip].stdout, tmp_queue),
            )

            # the thread will die with the end of the main procus
            tmp_thread.daemon = True
            # thread is launched
            tmp_thread.start()
            print(client_ip)
            self.game.network.ping[client_ip] = (tmp_thread, tmp_queue)
            self.game.playing = True

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
            for input in self.inputs:
                input.display_box()

            self.display_to_game()
            self.game.clock.tick(30)
