""" small game with udp feature

Raises:
    SystemError: arguments number not valid
"""
import pygame
import sys
import subprocess
import select


class Game:
    """Small game with two squares that interact with udp"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(5, 5)
        self.players = {}
        self.players["127.0.0.1:" + sys.argv[1]] = Player()
        self.players["127.0.0.1:" + sys.argv[1]].surface.fill((255, 0, 0))
        self.send = False
        self.my_port = sys.argv[1]
        self.my_ip = str("127.0.0.1:" + self.my_port)
        self.client_port = []
        if len(sys.argv) == 3:
            self.client_port = [sys.argv[2]]
            msg = str("first 127.0.0.1:" + self.my_port)
            self.client(msg)
            self.players[sys.argv[2]] = Player()
        self.serv = subprocess.Popen(
            ["./udpserver", self.my_port],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # interface between serv and python check readme for more info
        self.serv_value = select.poll()
        self.serv_value.register(self.serv.stdout, select.POLLIN)

    def events(self):
        """handle user interaction"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
        if self.send and self.client_port:
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
            msg = (
                "move " + self.my_ip + " " + str(self.players[self.my_ip].pos)
            )
        for ip in self.client_port:
            ip = ip.split(":")

            tmp = ["./udpclient", *ip, msg]
            subproc = subprocess.Popen(
                tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subproc.wait()

    def ip_send(self, target_ip):
        for ip in self.client_port:
            ip = ip.split(":")

            tmp = ["./udpclient", *ip, str("ip " + target_ip)]
            subproc = subprocess.Popen(
                tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subproc.wait()
        tmp = target_ip.split(":")
        for ip in self.client_port:
            msg = ["./udpclient", *tmp, str("ip " + ip)]
            subproc = subprocess.Popen(
                msg,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subproc.wait()
            msg = [
                "./udpclient",
                *tmp,
                str("move " + ip + " " + str(self.players[ip].pos)),
            ]
            subproc = subprocess.Popen(
                msg,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subproc.wait()

        msg2 = [
            "./udpclient",
            *tmp,
            str(
                "move " + self.my_ip + " " + str(self.players[self.my_ip].pos)
            ),
        ]
        subproc = subprocess.Popen(
            msg2,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subproc.wait()

    def server(self):
        """interprets the server's output"""
        out = self.serv_value.poll(0)
        # if out refers to something, it means that there is something on serv.stdout and that we can read without blocking the program
        if out:
            # reads the binary flux until '\n'
            line = self.serv.stdout.readline()
            # transforms the binary flux into string
            line = line.decode("ascii")
            line = line[:-1]
            if line.startswith("first"):
                line = line.split(" ")
                self.players[line[1]] = Player()
                self.ip_send(line[1])
                self.client_port.append(line[1])
            elif line.startswith("ip"):
                line = line.split(" ")
                self.client_port.append(line[1])
                if line[1] not in self.players:
                    self.players[line[1]] = Player()
            elif line.startswith("move"):
                line = line.split(" ")
                tmp = line[2] + " " + line[3]
                list_pos = tmp.strip("][").split(", ")
                for cmpt in range(len(list_pos)):
                    list_pos[cmpt] = int(list_pos[cmpt])
                self.players[line[1]].pos = list_pos
            elif line.startswith("disconnect"):
                line = line.split(" ")
                del self.players[line[1]]
                self.client_port.remove(line[1])

            # removes the '\n' from the string


class Player:
    def __init__(self):
        self.pos = [0, 0]
        self.surface = pygame.Surface((50, 50))
        self.surface.fill((0, 255, 0))


if len(sys.argv) not in (2, 3):
    raise SystemError("argc")
g = Game()
while True:
    g.run()
