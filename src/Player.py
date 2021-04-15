from src.config.window import TILE_SIZE, RESOLUTION
from src.utils.astar import aStarSearch
import pygame as pg


class Player:
    def __init__(self, map):
        self.map = map
        self.image = pg.image.load("src/assets/player.png")
        self.tileX = 2  # Will have to put map start point here
        self.tileY = 2
        self.futur_steps = []  # Will contain list of tile to go trough

    def draw(self, display):
        """Draw the player on the display"""
        s_width, s_height = RESOLUTION
        display.blit(self.image, (s_width // 2, s_height // 2))

    def move(self):
        """Move the player to X,Y (counted in tiles)"""
        if len(self.futur_steps) != 0:
            print("Walkin' ...")
            self.tileX, self.tileY = self.futur_steps.pop(0)

    def handle_event(self):
        """Check if needs to move and do so"""
        if pg.key.get_pressed()[pg.K_z]:
            self.tileY = max(self.tileY - 1, 0)
        if pg.key.get_pressed()[pg.K_s]:
            self.tileY = min(self.tileY + 1, len(self.map.map) - 1)
        if pg.key.get_pressed()[pg.K_d]:
            self.tileX = min(self.tileX + 1, len(self.map.map[1]) - 1)
        if pg.key.get_pressed()[pg.K_q]:
            self.tileX = max(self.tileX - 1, 0)
        self.map.centered_in = [self.tileX, self.tileY]

    def update_path(self, dest):
        self.futur_steps.clear()
        lastX, lastY = self.tileX, self.tileY
        act_sum = {
            'UL': (- 1, - 1), 'UR': (+ 1, - 1), 'DL': (- 1, + 1), 'DR': (+ 1, + 1),
            'U': (0, - 1), 'D': (0, + 1), 'L': (- 1, 0), 'R': (+ 1, 0)}
        direction_list = aStarSearch((lastX, lastY), dest, self.map)

        for action in direction_list:
            step = (lastX + act_sum[action][0], lastY + act_sum[action][1])
            lastX, lastY = step
            self.futur_steps.append(step)

        print("UPDATE:", self.futur_steps)
