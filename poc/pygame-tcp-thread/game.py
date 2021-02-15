""" small game with tcp feature

Raises:
    SystemError: arguments number not valid
"""
import pygame
import sys
import subprocess
import os
import signal
import threading
import time
import queue
import socket


class Game:
    """Small game with two squares that interact with tcp"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        self.clock = pygame.time.Clock()
        self.tick_cpt = 0
        pygame.key.set_repeat(5, 5)

        # sys.argv[1] refered to the server port of the program
        self.my_port = 8000

        # send a request to 8.8.8.8 to know the ip adress from the computer and stores it in tmp_ip to attribute it after.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # ping 8.8.8.8
        tmp_ip = s.getsockname()[0]

        # check if default port is already used
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        location = (tmp_ip, self.my_port)
        result_of_check = a_socket.connect_ex(location)
        while result_of_check == 0:
            self.my_port += 1
            location = (tmp_ip, self.my_port)
            result_of_check = a_socket.connect_ex(location)
        self.my_port = str(self.my_port)

        # ip stored in self.my_ip (exemple : 127.0.0.1:8000)
        self.my_ip = str(str(tmp_ip) + ":" + self.my_port)
        print(self.my_ip)

        # client_ip_port is a set to avoid duplicate. it contains ip string (exemple : {"127.0.0.1:8000","127.0.0.1:8001"})
        self.client_ip_port = set()
        # connections is a dictionnary that contains all the tcpclient subprocess. Keys are the ip:port
        self.connections = {}

        # players is a dictionnary that contains all the player. Keys are the ip:port
        self.players = {}
        self.players[self.my_ip] = Player()
        # Main player is in red to recognize it
        self.players[self.my_ip].surface.fill((255, 0, 0))

        # boolean to know if the program needs to send data
        self.send = False

        if len(sys.argv) == 2:  # you try to connect to someone
            # sys.argv[2] is ip:port
            self.client_ip_port.add(sys.argv[1])
            # split the ip:port to obtains ip and port
            tmp = sys.argv[1].split(":")
            # initialize a connection to ip contained in sys.argv[2]
            self.connections[sys.argv[1]] = subprocess.Popen(
                ["./tcpclient", tmp[0], tmp[1]],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # encode in binary a message that contains : first + client ip:port
            msg = str("first " + str(tmp_ip) + ":" + self.my_port + "\n")
            msg = str.encode(msg)
            # write the encoded message on stdin then flush it to avoid conflict
            self.connections[sys.argv[1]].stdin.write(msg)
            self.connections[sys.argv[1]].stdin.flush()
            # create a player associated to the client that you are connecting to
            self.players[sys.argv[1]] = Player()

        # create a subprocess that will execute the server. We will communicate with it by reading stdout
        self.serv = subprocess.Popen(
            ["./tcpserver", self.my_port, str(tmp_ip)],
            stdin=subprocess.PIPE,
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
        self.movement()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # inform other clients that the player has disconnected
                self.disconnect()
                pygame.quit()
                sys.exit(1)

    def run(self):
        """game loop that execute all necessary function"""
        if (
            self.send and self.client_ip_port and self.tick_cpt % 6 == 0
        ):  # if there is data to send and someone that can receive data
            self.client()
        self.clock.tick(60)
        self.tick_cpt += 1
        self.events()
        self.draw()
        self.server()

    def draw(self):
        """displays the players on the screen relative to their position"""
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption("FPS: " + str(int(self.clock.get_fps())))
        for player in self.players.values():
            self.screen.blit(player.surface, player.pos)
        pygame.display.flip()

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
            msg = str("move " + ip + " " + str(self.players[ip].pos) + "\n")
            msg = str.encode(msg)
            self.connections[target_ip].stdin.write(msg)
            self.connections[target_ip].stdin.flush()

        # send the position of the main player
        msg = str(
            "move "
            + self.my_ip
            + " "
            + str(self.players[self.my_ip].pos)
            + "\n"
        )
        msg = str.encode(msg)
        self.connections[target_ip].stdin.write(msg)
        self.connections[target_ip].stdin.flush()

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
                # get the line split by word
                line = line.split(" ")
                self.players[line[1]] = Player()
                # split the ip and the port
                tmp = line[1].split(":")
                # add a new connection to the connections dictionnary
                self.connections[line[1]] = subprocess.Popen(
                    ["./tcpclient", tmp[0], tmp[1]],
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
                if line[1] not in self.players:
                    self.players[line[1]] = Player()
                tmp = line[1].split(":")
                self.connections[line[1]] = subprocess.Popen(
                    ["./tcpclient", tmp[0], tmp[1]],
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
                if line[1] not in self.players:
                    self.players[line[1]] = Player()
                # add to the right player the associate position
                self.players[line[1]].pos = list_pos

            elif line.startswith("disconnect"):
                line = line.split(" ")
                # delete the player so it is not blit anymore
                del self.players[line[1]]
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

    def movement(self):
        """handle the movement of the player"""
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


def sigint_handler(sig, frame):
    pass


if len(sys.argv) not in (1, 2):
    raise SystemError("argc")
signal.signal(signal.SIGINT, sigint_handler)
g = Game()
while True:
    g.run()
