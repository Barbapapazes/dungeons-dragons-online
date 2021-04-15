from src.config.window import TILE_SIZE, RESOLUTION
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

dict_img_obj = {
    "firecamp": pg.image.load("src/assets/objects/firecamp.png"),
    "chestC": pg.image.load("src/assets/objects/chestClosed.png"),
    "chestO": pg.image.load("src/assets/objects/chestOpen.png")
}


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


"""
class Doors:
    "Define doors (portals) in maps"

    def __init__(self, side1, map1, side2, map2):
        self.side1 = side1  # coordonate of a side of the door in tiles
        self.map1 = map1  # map of a side of a door
        self.side2 = side2  # coordonate of a side of the other door in tiles
        self.map2 = map2  # map of the otehr side of the other door

    def is_inside(self, mapid, x, y, mx, my, player_list, map):
        "check if a player is inside the door and clicking on it. If so switch the map"
        # check side 1
        if mapid == self.map1 and all(
            (self.side1[0] * TILE_SIZE <= px < (self.side1[0] + 1) * TILE_SIZE)
            and (
                self.side1[1] * TILE_SIZE
                <= py
                < (self.side1[1] + 1) * TILE_SIZE
            )
            for px, py in [[x, y], [mx, my]]
        ):
            map.switch(self.map2, self.side2, player_list)
            return True
        # check the side 2
        if mapid == self.map2 and all(
            (self.side2[0] * TILE_SIZE <= px < (self.side2[0] + 1) * TILE_SIZE)
            and (
                self.side2[1] * TILE_SIZE
                <= py
                < (self.side2[1] + 1) * TILE_SIZE
            )
            for px, py in [[x, y], [mx, my]]
        ):
            map.switch(self.map1, self.side1, player_list)
            return True
        return False
"""


class Map:
    "Define maps for the current game"

    def __init__(self, file):
        ### Getting tiles, start position and doors infos from file ###
        with open(file) as f_map:
            map_lines = [line for line in f_map]
        self.name = map_lines[0][:-1]
        # Note : self.map contain all map sorted as [dungeon number][floor number][Y][X]
        # X is the position in the Y line
        main_map = [
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
        self.map = main_map
        ### Setting minimap ###
        # Not done yet
        self.init_views()

    def init_views(self):
        """Init array of every surface to blit on the screen (tiles & vision)"""
        lenX, lenY = len(self.map[0]), len(self.map)
        display = pg.Surface((lenX * TILE_SIZE, lenY * TILE_SIZE))
        for tileY in range(lenY):
            for tileX in range(lenX):
                display.blit(
                    self.map[tileY][tileX].image,
                    (tileX * TILE_SIZE, tileY * TILE_SIZE),
                )
        self.map_canva = display
        # self.mini_canva_list = []
        # add view list here

    def draw(self, display, x, y):
        "draw a part of map center in x,y (x and y being couted in tiles"
        s_width, s_height = RESOLUTION
        display.blit(
            self.map_canva,
            (-x * TILE_SIZE + s_width / 2, -y * TILE_SIZE + s_height / 2),
        )  # display the carpet at the right place


class MapObject:
    """A class of object on map"""

    def __init__(self, tile):
        self.tileX, self.tileY = tile

    def activable(self, player_posX, player_posY):
        """Return weather the player can activate the object or not""""
        return (abs(self.tileX - player_posX) < 2 and abs(self.tileY - player_posY) < 2)


class Firecamp(MapObject):
    def __init__(self, tile):
        """Initiate a firecamp"""
        MapObject.__init__(tile)
        self.image = dict_img_obj["firecamp"].convert()

    def use(self, player):
        if(self.activable(player.tileX, player.tileY)):
            # ++ player health
            pass


class Chest(MapObject):
    def __init__(self, tile):
        MapObject.__init__(tile)
        self.image = dict_img_obj["chestC"].convert()
        self.obj_list = []
        # generate obj list

    def isEmpty(self):
        return (len(self.obj_list) == 0)

    def use(self, player):
        if not self.isEmpty():
            # give player obj here
            self.image = dict_img_obj["chestO"].convert()
            pass
