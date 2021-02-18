import pygame as pg


class Player:
    """A player with a position in coordonate and on wich map he is"""

    def __init__(self, i, j, map):
        self.x = i
        self.y = j
        self.map = map

    def draw(self, display):
        pg.draw.rect(
            display,
            [255, 0, 0],
            [self.x * 20, self.y * 20, 20, 20],
        )


class PlayerList:
    """regroup all players with a fonction to swap from one to an other and one to display them"""

    def __init__(self, tab, map):
        self.players = [
            Player(tab[i], tab[i + 1], map) for i in range(len(tab) // 2)
        ]
        self.count = 0
        self.cplayer = self.players[self.count]

    def nextplayer(self):
        self.count = (self.count + 1) % len(self.players)
        self.cplayer = self.players[self.count]

    def draw(self, window, map):
        [p.draw(window) for p in self.players if map == p.map]
