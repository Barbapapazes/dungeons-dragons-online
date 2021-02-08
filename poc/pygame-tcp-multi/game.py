""" small game with tcp feature

Raises:
    SystemError: arguments number not valid
"""
import pygame
import sys
import subprocess
import select


class Game:
    """Small game with two squares that interact with tcp"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(5, 5)
        self.players = {}
        self.players["player1"] = Player()
        self.players["player2"] = Player()
        self.players["player1"].surface.fill((255, 0, 0))  # red
        self.players["player2"].surface.fill((0, 255, 0))  # green
        self.send = False
        self.my_port = sys.argv[1]
        self.client_port = sys.argv[2]
        self.serv = subprocess.Popen(
            ["./tcpserver", self.my_port],
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
                self.serv.terminate()  # kill the subprocess to avoid bind error
                pygame.quit()
                sys.exit(1)
            if (
                pygame.key.get_pressed()[pygame.K_s]
                and self.players["player1"].pos[1] + 50 < 768
            ):
                self.players["player1"].pos[1] += 1
                self.send = True
            if (
                pygame.key.get_pressed()[pygame.K_z]
                and self.players["player1"].pos[1] > 0
            ):
                self.players["player1"].pos[1] -= 1
                self.send = True
            if (
                pygame.key.get_pressed()[pygame.K_q]
                and self.players["player1"].pos[0] > 0
            ):
                self.players["player1"].pos[0] -= 1
                self.send = True
            if (
                pygame.key.get_pressed()[pygame.K_d]
                and self.players["player1"].pos[0] + 50 < 1024
            ):
                self.send = True
                self.players["player1"].pos[0] += 1

    def run(self):
        """game loop that execute all necessary function"""
        if self.send:
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

    def client(self):
        """create a subprocess that will send the position to the local server with client_port"""
        self.send = False
        subprocess.Popen(
            [
                "./tcpclient",
                self.client_port,
                str(self.players["player1"].pos),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def server(self):
        """interprets the server's output"""
        out = self.serv_value.poll(0)
        # if out refers to something, it means that there is something on serv.stdout and that we can read without blocking the program
        if out:
            # reads the binary flux until '\n'
            line = self.serv.stdout.readline()
            # transforms the binary flux into string
            line = line.decode("ascii")
            # removes the '\n' from the string
            line = line[:-1]
            # transform the string into list
            list_pos = line.strip("][").split(", ")
            # cast each element of the list to int
            for cmpt in range(len(list_pos)):
                list_pos[cmpt] = int(list_pos[cmpt])
            # attribute the new position
            self.players["player2"].pos = list_pos


class Player:
    def __init__(self):
        self.pos = [0, 0]
        self.surface = pygame.Surface((50, 50))


if len(sys.argv) != 3:
    raise SystemError("argc")
g = Game()
while True:
    g.run()
