"""Join menu"""
import queue
import subprocess
import threading
import time
import os
import signal
import socket
from os import path


import pygame as pg
from src.config.assets import fonts_folder, menus_folder
from src.config.colors import WHITE
from src.interface import Button, Input, Text
from src.menu._menu import Menu

from src.utils.network import enqueue_output


class MenuJoin(Menu):
    """Menu to join a game"""

    def __init__(self, game):
        Menu.__init__(self, game)

        self.menu_background = pg.image.load(
            path.join(menus_folder, "background.png")
        ).convert_alpha()

        self.input_text = Text(
            self.game.display,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 - 35,
            "Enter IP to join a game :",
            path.join(fonts_folder, "CascadiaCode.ttf"),
            WHITE,
            15,
            True,
        )

        self.ip_input = Input(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 20,
            400,
            50,
            path.join(fonts_folder, "CascadiaCode.ttf"),
            32,
            25,
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

        self.texts = [
            getattr(self, text)
            for text in dir(self)
            if isinstance(getattr(self, text), Text)
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
            if not self.isOpen(tmp[0], tmp[1]):
                return
            print("client", client_ip)
            # initialize a connection to ip contained in sys.argv[2]
            self.game.network._client.stdin.write(
                str.encode("!" + client_ip + "\n")
            )

            self.game.network._client.stdin.flush()
            self.displaying = False
            self.game.menu_running = False
            # unpause the server
            os.kill(self.game.network._server.pid, signal.SIGUSR2)
            self.game.network.client_ip_port.add(client_ip)
            # split the ip:port to obtains ip and port
            tmp = client_ip.split(":")
            # initialize a connection to ip contained in sys.argv[2]
            # encode in binary a message that contains : first + client ip:port
            msg = str(
                str(self.game.own_id)
                + " 0 "
                + str(self.game.network.ip)
                + ":"
                + str(self.game.network.port)
            )
            self.game.network.send_message(msg, client_ip)
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
            for text in self.texts:
                text.display_text()

            self.display_to_game()
            self.game.clock.tick(30)

    def isOpen(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            t = s.connect((ip, int(port)))
            s.shutdown(2)
            return True
        except:
            return False
