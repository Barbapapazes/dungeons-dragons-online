"""This file contains the implementation of simple menus"""
from .interface import Button, TextEntry
import pygame as pg
import time
import subprocess


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
        self.join_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 150,
            "Join",
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
        self.button_list = [
            getattr(self, button)
            for button in dir(self)
            if isinstance(getattr(self, button), Button)
        ]

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
        if self.join_button.is_clicked(event):
            self.game.current_menu = self.game.join_menu
            self.displaying = False
        if self.return_button.is_clicked(event):
            self.game.current_menu = self.game.main_menu
            self.displaying = False

    def display_menu(self):
        """ Displays the menu on our screen"""
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


class JoinMenu(Menu):
    """Menu to join a game"""

    def __init__(self, game):
        Menu.__init__(self, game)

        self.menu_background = pg.image.load(
            "src/assets/menus/background.png"
        ).convert_alpha()

        self.ip_input = TextEntry(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2,
            200,
            50,
            "src/fonts/enchanted_land.otf",
            32,
            20,
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

        self.join_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 150,
            "Join",
            "src/fonts/enchanted_land.otf",
            "#000000",
            40,
        )

        self.button_list = [
            getattr(self, button)
            for button in dir(self)
            if isinstance(getattr(self, button), Button)
        ]

        self.textentry_list = [
            getattr(self, textentry)
            for textentry in dir(self)
            if isinstance(getattr(self, textentry), TextEntry)
        ]

    def check_events(self, event):
        """[summary] This method deals with the user inputs
            on the different buttons of the menu
        Args:
            event ([type]): [description] a pygame event
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
            self.game.playing = True
            self.game.client_ip_port.add(client_ip)
            # split the ip:port to obtains ip and port
            tmp = client_ip.split(":")
            # initialize a connection to ip contained in sys.argv[2]
            self.game.connections[client_ip] = tmp_proc
            tmp = self.game.my_ip.split(":")
            # encode in binary a message that contains : first + client ip:port
            msg = str("first " + str(tmp[0]) + ":" + tmp[1] + "\n")
            msg = str.encode(msg)
            # write the encoded message on stdin then flush it to avoid conflict
            self.game.connections[client_ip].stdin.write(msg)
            self.game.connections[client_ip].stdin.flush()

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
            for textentry in self.textentry_list:
                textentry.display_box()

            self.display_to_game()
            self.clock.tick(30)
