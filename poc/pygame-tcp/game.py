import pygame
import sys
import subprocess


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(5, 5)
        self.pos = [0, 0]
        self.surface = pygame.Surface((50, 50))
        self.surface.fill((255, 255, 255))
        self.send = False

    def events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(1)
            if pygame.key.get_pressed()[pygame.K_s] and self.pos[1] + 50 < 768:
                self.pos[1] += 1
                self.send = True
            if pygame.key.get_pressed()[pygame.K_z] and self.pos[1] > 0:
                self.pos[1] -= 1
                self.send = True
            if pygame.key.get_pressed()[pygame.K_q] and self.pos[0] > 0:
                self.pos[0] -= 1
                self.send = True
            if (
                pygame.key.get_pressed()[pygame.K_d]
                and self.pos[0] + 50 < 1024
            ):
                self.send = True
                self.pos[0] += 1

    def run(self):
        if self.send:
            self.serv()
        self.tick = self.clock.tick(60) / 1000
        self.events()
        self.draw()
        self.auto()

    def auto(self):
        self.pos[1] += 1
        self.pos[0] += 1
        self.send = True

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.surface, self.pos)
        pygame.display.flip()

    def serv(self):
        self.send = False
        subprocess.Popen(
            ["./tcpclient", str(self.pos)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


g = Game()
while True:
    g.run()
