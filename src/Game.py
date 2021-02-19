"""This file contains the Game class which is the central element of
our game"""
import pygame as pg
import sys
import subprocess
import os
import signal
import threading
import time
import queue
import socket
from .Settings import RESOLUTION
from .Menu import CharacterMenu, MainMenu, JoinMenu


class Game(object):
    """The game class"""

    def __init__(self):

        self.running = True
        self.playing = False
        self.menu_running = True

        self.resolution = RESOLUTION
        self.window = pg.display.set_mode(self.resolution)

        # self.display is basically the canvas in which we blit everything
        self.display = pg.Surface(self.resolution)
        self.background = pg.image.load(
            "src/assets/menus/background.png"
        ).convert_alpha()
        self.background = pg.transform.scale(self.background, RESOLUTION)
        self.display.blit(self.background, (0, 0))
        pg.display.set_caption("Donjons & Python")

        # ------MENUS------ #
        self.main_menu = MainMenu(self)
        self.character_menu = CharacterMenu(self)
        # The current menu is the menu we always display
        self.current_menu = self.main_menu
        self.join_menu = JoinMenu(self)

        self.clock = pg.time.Clock()

        self.my_port = 8000

        # send a request to 8.8.8.8 to know the ip adress from the computer and stores it in tmp_ip to attribute it after.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # ping 8.8.8.8
        tmp_ip = s.getsockname()[0]

        # check if default port is already used

        self.serv = subprocess.Popen(
            ["./src/tcpserver", str(self.my_port), str(tmp_ip)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(0.1)
        poll = self.serv.poll()
        while poll is not None:
            self.my_port += 1
            self.serv = subprocess.Popen(
                ["./src/tcpserver", str(self.my_port), str(tmp_ip)],
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
        # create a subprocess that will execute the server. We will communicate with it by reading stdout

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

    def check_events(self):
        "Checks for events in our game"
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.current_menu.displaying = False
                self.running, self.playing = False, False
                self.disconnect()
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
        self.disconnect()

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
            self.server()

    def server(self):
        """interprets the server's output"""
        try:
            # try to pop something from the queue if there is nothing at the end of the timeout raise queue.Empty
            line = self.q.get(timeout=0.005)
        except queue.Empty:
            return
        else:
            print(line)
            # if no exception is raised then line contains something
            line = line.decode("ascii")  # binary flux that we need to decode
            line = line[:-1]  # delete the final `\n`

            # first connection of a client
            if line.startswith("first"):
                # get the line split by word
                line = line.split(" ")
                # self.players[line[1]] = Player()
                # split the ip and the port
                tmp = line[1].split(":")
                # add a new connection to the connections dictionnary
                self.connections[line[1]] = subprocess.Popen(
                    ["./src/tcpclient", tmp[0], tmp[1]],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                self.first_connection(line[1])
                # add the new ip to the client_ip_port set
                self.client_ip_port.add(line[1])

            # if an ip is sent, add it to the set
            elif line.startswith("ip"):
                line = line.split(" ")
                self.client_ip_port.add(line[1])
                # if line[1] not in self.players:
                #     self.players[line[1]] = Player()
                tmp = line[1].split(":")
                self.connections[line[1]] = subprocess.Popen(
                    ["./src/tcpclient", tmp[0], tmp[1]],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            # if a movement is sent
            elif line.startswith("move"):
                # split the line with ` `
                line = line.split(" ")
                # position is separate in two different index so we concatenate them
                tmp = line[2] + " " + line[3]
                # transform the string into list of string
                list_pos = tmp.strip("][").split(", ")
                # transform the list of string into list of int
                for cmpt in range(len(list_pos)):
                    list_pos[cmpt] = int(list_pos[cmpt])
                # if players doesn't exist create it
                #  if line[1] not in self.players:
                # self.players[line[1]] = Player()
                # add to the right player the associate position
                self.players[line[1]].pos = list_pos

            elif line.startswith("disconnect"):
                line = line.split(" ")
                # delete the player so it is not blit anymore
                # del self.players[line[1]]
                # delete his ip
                self.client_ip_port.remove(line[1])
                pid = self.connections[line[1]].pid
                os.kill(pid, signal.SIGINT)
                del self.connections[line[1]]

    def disconnect(self):
        """handle the disconnection of the client and end all the subprocess"""
        # sends to all other players that the client has disconnected
        self.client(str("disconnect " + self.my_ip + "\n"))
        # ensure that the disconnect message has been sent
        time.sleep(0.5)
        # end the serv process (look for tcpserver to get more details)
        os.kill(self.serv.pid, signal.SIGUSR1)
        for ip in self.connections:
            # end all the tcpclient process that are in connections dictionnary
            os.kill(self.connections[ip].pid, signal.SIGUSR1)

    def client(self, msg=None):
        """create a subprocess that will send the position to the local server with client_ip_port"""
        self.send = False

        if msg is None:
            # If no message is specified then we send the position of the client
            msg = (
                "move "
                + self.my_ip
                + " "
                + str(self.players[self.my_ip].pos)
                + "\n"
            )
        msg = str.encode(msg)

        for ip in self.client_ip_port:
            # write the encoded message on the right tcpclient stdin then flush it to avoid conflict
            self.connections[ip].stdin.write(msg)
            self.connections[ip].stdin.flush()

    def first_connection(self, target_ip):
        """Define what the program does when a new connection occures

        Args:
            target_ip (str): string that contains the ip:port of the new connection
        """
        for ip in self.client_ip_port:
            # this loop sends to all other client the information (<ip>:<port>) of the new player
            msg = str("ip " + target_ip + "\n")
            msg = str.encode(msg)
            self.connections[ip].stdin.write(msg)
            self.connections[ip].stdin.flush()

        for ip in self.client_ip_port:
            # this loop sends to the new user all the ip contained in self.client_ip_port and all the relative position of the players
            # block that sends the ip
            msg = str("ip " + ip + "\n")
            msg = str.encode(msg)
            self.connections[target_ip].stdin.write(msg)
            self.connections[target_ip].stdin.flush()

            # block that sends the position
            # msg = str("move " + ip + " " + str(self.players[ip].pos) + "\n")
            # msg = str.encode(msg)
            # self.connections[target_ip].stdin.write(msg)
            # self.connections[target_ip].stdin.flush()

        # send the position of the main player
        # msg = str(
        #     "move "
        #     + self.my_ip
        #     + " "
        #     + str(self.players[self.my_ip].pos)
        #     + "\n"
        # )
        # msg = str.encode(msg)
        # self.connections[target_ip].stdin.write(msg)
        # self.connections[target_ip].stdin.flush()


def enqueue_output(out, queue_line):
    """Queued the first line from stdout in the queue passed in parameter

    Args:
        out (int): file descriptor where the function will read
        queue_line (queue.Queue()): FIFO queue
    """
    for line in iter(out.readline, b""):
        queue_line.put(line)
