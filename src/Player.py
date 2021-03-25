from src.config.window import TILE_SIZE, RESOLUTION
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

    def move(self, X, Y):
        """Move the player to X,Y (counted in tiles)"""
        self.tileX = X
        self.tileY = Y

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
