""" small game with tcp feature

Raises:
    SystemError: arguments number not valid
"""
import pygame
import sys
import subprocess
import select
import threading
import queue
import socket


class Game:
    """Small game with two squares that interact with tcp"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(5, 5)

        self.my_port = sys.argv[1]
        # send a request to 8.8.8.8 to know the ip adress from the computer
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        tmp_ip = s.getsockname()[0]
        self.my_ip = str(str(tmp_ip) + ":" + self.my_port)
        print(self.my_ip)
        self.client_port = set()

        self.players = {}
        self.players[self.my_ip] = Player()
        # Main player is in red to recognize it
        self.players[self.my_ip].surface.fill((255, 0, 0))

        # boolean to know if the program needs to send data
        self.send = False

        if len(sys.argv) == 3:  # you try to connect to someone
            self.client_port.add(sys.argv[2])
            msg = str("first " + str(tmp_ip) + ":" + self.my_port)
            self.client(msg)
            self.players[sys.argv[2]] = Player()

        self.serv = subprocess.Popen(
            ["./tcpserver", self.my_port, str(tmp_ip)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

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

    def events(self):
        """handle user interaction"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # inform other clients that the player has disconnected
                self.client(str("disconnect " + self.my_ip))
                self.serv.terminate()  # kill the subprocess to avoid bind error
                pygame.quit()
                sys.exit(1)
            if (
                pygame.key.get_pressed()[pygame.K_s]
                and self.players[self.my_ip].pos[1] + 50 < 768
            ):
                self.players[self.my_ip].pos[1] += 1
                self.send = True
            if (
                pygame.key.get_pressed()[pygame.K_z]
                and self.players[self.my_ip].pos[1] > 0
            ):
                self.players[self.my_ip].pos[1] -= 1
                self.send = True
            if (
                pygame.key.get_pressed()[pygame.K_q]
                and self.players[self.my_ip].pos[0] > 0
            ):
                self.players[self.my_ip].pos[0] -= 1
                self.send = True
            if (
                pygame.key.get_pressed()[pygame.K_d]
                and self.players[self.my_ip].pos[0] + 50 < 1024
            ):
                self.send = True
                self.players[self.my_ip].pos[0] += 1

    def run(self):
        """game loop that execute all necessary function"""
        if (
            self.send and self.client_port
        ):  # if there is data to send and someone that can receive data
            self.client()
        self.tick = self.clock.tick(60) / 1000
        self.events()
        self.draw()
        self.server()
        # self.auto()

    def auto(self):
        """Moves the player automaticaly"""
        self.players["player1"].pos[1] += 1
        self.players["player1"].pos[0] += 1
        self.send = True

    def draw(self):
        """displays the players on the screen relative to their position"""
        self.screen.fill((0, 0, 0))
        for player in self.players.values():
            self.screen.blit(player.surface, player.pos)
        pygame.display.flip()

    def client(self, msg=None):
        """create a subprocess that will send the position to the local server with client_port"""
        self.send = False

        if msg is None:
            # If no message is specified a data
            msg = (
                "move " + self.my_ip + " " + str(self.players[self.my_ip].pos)
            )

        for ip in self.client_port:
            # ip is associated with a port <ip>:<port>
            ip = ip.split(":")
            # tmp contains ["./tcpclient",ip,port, msg]
            tmp = ["./tcpclient", *ip, msg]
            # execute the command contained in tmp
            subprocess.Popen(
                tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

    def first_connection(self, target_ip):
        """Define what the program does when a new connection occures

        Args:
            target_ip (str): string that contains the ip:port of the new connection
        """
        for ip in self.client_port:
            # this loop sends to all other client the information (<ip>:<port>) of the new player
            ip = ip.split(":")
            tmp = ["./tcpclient", *ip, str("ip " + target_ip)]
            subprocess.Popen(
                tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        # split the target ip to send to it all the information of the current state of the game
        tmp = target_ip.split(":")
        for ip in self.client_port:
            # this loop send to the new user all the ip contained in self.client_port and the position of all the players
            # send ip
            msg = ["./tcpclient", *tmp, str("ip " + ip)]
            subprocess.Popen(
                msg,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # send pos
            msg = [
                "./tcpclient",
                *tmp,
                str("move " + ip + " " + str(self.players[ip].pos)),
            ]
            subprocess.Popen(
                msg,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        # send the position of the main player
        msg2 = [
            "./tcpclient",
            *tmp,
            str(
                "move " + self.my_ip + " " + str(self.players[self.my_ip].pos)
            ),
        ]
        subprocess.Popen(
            msg2,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def server(self):
        """interprets the server's output"""
        try:
            # try to pop something from the queue if there is nothing at the end of the timeout raise queue.Empty
            line = self.q.get(timeout=0.005)
        except queue.Empty:
            return
        else:
            # if no exception is raised then line contains something
            line = line.decode("ascii")  # binary flux that we need to decode
            line = line[:-1]  # delete the final `\n`
            # first connection of a client
            if line.startswith("first"):
                line = line.split(" ")
                self.players[line[1]] = Player()
                self.first_connection(line[1])
                self.client_port.add(line[1])
            # if an ip is sent, add it to the set
            elif line.startswith("ip"):
                line = line.split(" ")
                self.client_port.add(line[1])
                if line[1] not in self.players:
                    self.players[line[1]] = Player()
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
                if line[1] not in self.players:
                    self.players[line[1]] = Player()
                # add to the right player the associate position
                self.players[line[1]].pos = list_pos

            elif line.startswith("disconnect"):
                line = line.split(" ")
                # delete the player so it is not blit anymore
                del self.players[line[1]]
                # delete his ip
                self.client_port.remove(line[1])


class Player:
    def __init__(self):
        self.pos = [0, 0]
        self.surface = pygame.Surface((50, 50))
        self.surface.fill((0, 255, 0))


def enqueue_output(out, queue_line):
    """Queued the first line from stdout in the queue passed in parameter

    Args:
        out (int): file descriptor where the function will read
        queue_line (queue.Queue()): FIFO queue
    """
    for line in iter(out.readline, b""):
        queue_line.put(line)
    out.close()


if len(sys.argv) not in (2, 3):
    raise SystemError("argc")
g = Game()
while True:
    g.run()
