import pygame as pg


class Map:
    """just a regular map with a draw func"""

    def __init__(self, map):
        self.cmap = map

    def draw(self, display):
        [
            [
                pg.draw.rect(
                    display,
                    [255 * self.cmap[i][j]] * 3,
                    [i * 20, j * 20, 20, 20],
                )
                for j in range(len(self.cmap[0]))
                for i in range(len(self.cmap))
            ]
        ]
