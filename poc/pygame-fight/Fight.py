import pygame as pg
from Map import Map


class Fight:
    """ When a fight start we create the arena where evry fighter will go then we put evry one in it"""

    def __init__(self, player, game, i):
        self.game = game
        self.x = player.x
        self.y = player.y
        self.nbr = i
        self.map = [
            [
                self.game.map.cmap[i][j]
                for j in range(
                    max(0, player.y - 2),
                    min(len(self.game.map.cmap[0]), player.y + 3),
                )
            ]
            for i in range(
                max(0, player.x - 2),
                min(len(self.game.map.cmap), player.x + 3),
            )
        ]
        self.cmap = (
            [[0 for _ in range(len(self.map[0]) + 2)]]
            + [[0] + self.map[i] + [0] for i in range(len(self.map))]
            + [[0 for _ in range(len(self.map[0]) + 2)]]
        )
        self.fmap = Map(self.cmap)

        detect = [
            [player.x + i, player.y + j]
            for i in range(-2, 3)
            for j in range(-2, 3)
        ]
        for p in game.plist.players:
            if p != player and [p.x, p.y] in detect:
                p.map = ["f", i]
                p.x = len(self.cmap) // 2
                p.y = len(self.cmap[0]) // 2
        for f in game.flist.foes:
            if [f.x, f.y] in detect:
                f.map = ["f", i]
                f.x = len(self.cmap) // 2
                f.y = len(self.cmap[0]) // 2

        player.map = ["f", i]
        player.x = len(self.cmap) // 2
        player.y = len(self.cmap[0]) // 2


class FightList:
    """Regroup all the fight that are appening (no ways to rxit or stop one at the moment), when a new fight is created we add a warp point on the map"""

    def __init__(self):
        self.flist = []
        self.nbrfight = 0

    def newfight(self, player, game):
        self.flist.append(Fight(player, game, self.nbrfight))
        self.nbrfight += 1

    def new_challenger(self, plist):
        for p in plist.players:
            if p.map[0] == "m":
                for f in self.flist:
                    if (p.x, p.y) == (f.x, f.y):
                        p.map = ["f", f.nbr]
                        p.x = len(f.cmap) // 2
                        p.y = len(f.cmap[0]) // 2

    def draw(self, display):
        [
            pg.draw.rect(display, (255, 140, 0), [f.x * 20, f.y * 20, 20, 20])
            for f in self.flist
        ]
