from src.config.window import TILE_SIZE, RESOLUTION
from src.config.colors import DARKBROWN
import pygame as pg
from random import randint

### Tiles sprite managing ###
wall_list = ["W", "V"]
dict_tile_list = {
    "-": [f"simple{i}.jpg" for i in range(1, 21)],
    "D": [f"dirt{i}.jpg" for i in range(1, 14)],
    "V": ["void.jpg"],
    "W": ["wall.jpg"],
    "P": ["stair.jpg"],
    "G": ["door.jpg"],
}
dict_tile_list_img = {}
for char in dict_tile_list:
    dict_tile_list_img[char] = [
        pg.image.load("src/assets/tiles/" + dict_tile_list[char][i])
        for i in range(len(dict_tile_list[char]))
    ]


class Tile:
    "Definition of tiles and properties"

    def __init__(self, char):
        self.char = char  # Character used in map.txt to represent
        self.wall = char in wall_list  # check if it is a wall
        if len(dict_tile_list_img[char]) > 1:
            self.image = dict_tile_list_img[char][
                randint(0, len(dict_tile_list_img[char]) - 1)
            ].convert()
            if char == "-" and randint(1, 5) != 3:
                self.image = dict_tile_list_img[char][19].convert()
        else:
            self.image = dict_tile_list_img[char][0].convert()
        # We convert our image so we can change the opacity
        self.mini_image = dict_tile_list_img[char][0].convert()
        self.mini_image = pg.transform.scale(
            self.mini_image, (TILE_SIZE // 16, TILE_SIZE // 16)
        )
        self.visible = (
            False  # Is this tile visible by one character at least ?
        )
        self.discovered = False  # Used for the minimap

    def update_visibility(self):
        "Change the visibility to VISIBLE"
        self.visible = True

    def update_mini_visibility(self):
        "Change the visibility for the mini_image"
        self.discovered = True


class Map:
    "Define maps for the current game"

    def __init__(self, file):
        ### Getting tiles, start position and doors infos from file ###
        with open(file) as f_map:
            map_lines = [line for line in f_map]
        self.name = map_lines[0][:-1]
        # Note : self.map contain all map sorted as [dungeon number][floor number][Y][X]
        # X is the position in the Y line
        self.map = [
            [
                Tile(map_lines[lineY][placeX])
                for placeX in range(len(map_lines[lineY][:-1]))
            ]
            for lineY in range(1, len(map_lines) - 23)
        ]
        self.start_point = [int(map_lines[-15][:-1]), int(map_lines[-14][:-1])]
        self.doors = [
            [int(map_lines[i][:-1]), int(map_lines[i + 1][:-1])]
            for i in range(-12, 0, 2)
        ]
        self.centered_in = [0, 0]  # X and Y where is centered
        ### Setting minimap ###
        minimap_reduction = 8
        s_width, s_height = RESOLUTION
        self.minimap_size = s_width // minimap_reduction, s_height // minimap_reduction

        self.minimap = pg.Surface(self.minimap_size, minimap_reduction)

        ###Setting canvas###
        self.init_views(self.minimap_size, minimap_reduction)

    def init_views(self, mini_size, mini_coeff):
        """Init array of every surface to blit on the screen (tiles & vision)"""
        lenX, lenY = len(self.map[0]), len(self.map)
        display = pg.Surface((lenX * TILE_SIZE, lenY * TILE_SIZE))
        self.mini_tile_s = TILE_SIZE // mini_coeff
        mini_display = pg.Surface(
            (lenX * self.mini_tile_s, lenY * self.mini_tile_s))
        for tileY in range(lenY):
            for tileX in range(lenX):
                display.blit(
                    self.map[tileY][tileX].image,
                    (tileX * TILE_SIZE, tileY * TILE_SIZE),
                )
                ### Minimap ###
                # Transform image in a mini image
                mini_img = pg.Surface.copy(self.map[tileY][tileX].image)
                pg.transform.scale(
                    mini_img, (self.mini_tile_s, self.mini_tile_s))

                mini_display.blit(
                    mini_img, (tileX * self.mini_tile_s, tileY * self.mini_tile_s))
        self.map_canva = display
        self.mini_canva = mini_display
        # self.mini_canva_list = []
        # add view list here

    def draw(self, display):
        "draw a part of map center in x,y (x and y being couted in tiles"
        s_width, s_height = RESOLUTION
        display.blit(
            self.map_canva,
            (-self.centered_in[0] * TILE_SIZE
             + s_width / 2, -self.centered_in[1] * TILE_SIZE + s_height / 2),
        )  # display the carpet at the right place

    def draw_mini(self, display):
        "Display a minimap"
        s_width, s_height = RESOLUTION
        self.minimap.fill(DARKBROWN)
        self.minimap.blit(self.mini_canva, (-self.centered_in[0] * self.mini_tile_s
                                            + self.minimap_size[0] / 2, -self.centered_in[1] * self.mini_tile_s + self.minimap_size[1] / 2))
        display.blit(self.minimap, (s_width - self.minimap_size[0] - 4, 4))
