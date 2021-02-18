import pygame as pg


class Foe:
    """ A lot like player but with an extra func to detect players"""

    def __init__(self, i, j, map):
        self.x = i
        self.y = j
        self.map = map

    def draw(self, display):
        [
            pg.draw.rect(
                display,
                [0, 0, 255],
                [(self.x + i) * 20, (self.y + j) * 20, 20, 20],
            )
            for j in range(-2, 3)
            for i in range(-2, 3)
            if i ** 2 + j ** 2 <= 4
        ]
        pg.draw.rect(
            display,
            [0, 255, 0],
            [self.x * 20, self.y * 20, 20, 20],
        )

    def check_player(self, plist, fight, game):
        for p in plist.players:
            if [p.x, p.y] in [
                [self.x + i, self.y + j]
                for j in range(-2, 3)
                for i in range(-2, 3)
                if i ** 2 + j ** 2 <= 4
            ]:
                return fight.newfight(p, game)


class FoeList:
    """ Regroup all enemies"""

    def __init__(self, tab, map):
        self.foes = [
            Foe(tab[i], tab[i + 1], map) for i in range(len(tab) // 2)
        ]

    def draw(self, window, map):
        [f.draw(window) for f in self.foes if map == f.map]

    def check_player(self, plist, fight, game):
        [
            f.check_player(plist, fight, game)
            for f in self.foes
            if f.map[0] != "f"
        ]
