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
        self.centered_in = [2, 2]  # X and Y where is centered
        ### Setting minimap ###
        minimap_reduction = 8
        self.s_width, self.s_height = RESOLUTION
        self.nb_tileX, self.nb_tileY = (
            self.s_width // TILE_SIZE) - 1, (self.s_height // TILE_SIZE) - 1
        self.minimap_size = self.s_width // minimap_reduction, self.s_height // minimap_reduction
        self.minimap = pg.Surface(self.minimap_size, minimap_reduction)
        ### Setting canvas ###
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
        display.blit(
            self.map_canva,
            (-self.centered_in[0] * TILE_SIZE
             + self.s_width / 2, -self.centered_in[1] * TILE_SIZE + self.s_height / 2),
        )  # display the carpet at the right place

    def draw_mini(self, display):
        "Display a minimap"
        self.minimap.fill(DARKBROWN)
        self.minimap.blit(self.mini_canva, (-self.centered_in[0] * self.mini_tile_s
                                            + self.minimap_size[0] / 2, -self.centered_in[1] * self.mini_tile_s + self.minimap_size[1] / 2))
        display.blit(self.minimap, (self.s_width
                                    - self.minimap_size[0] - 4, 4))

    def is_visible_tile(self, numX, numY):
        "Return if the tile is displayed"
        lim_X_left = self.centered_in[0] - self.nb_tileX // 2
        lim_X_right = self.centered_in[0] + self.nb_tileX // 2
        lim_Y_left = self.centered_in[1] - self.nb_tileY // 2
        lim_Y_right = self.centered_in[1] + self.nb_tileY // 2
        return ((lim_X_left <= numX <= lim_X_right) and (lim_Y_left <= numY <= lim_Y_right))

    def get_clicked_tile(self):
        """Return the clicked tile"""
        m_posX, m_posY = pg.mouse.get_pos()
        m_posX = self.centered_in[0] - \
            (self.nb_tileX // 2) + (m_posX // TILE_SIZE) - 1
        m_posY = self.centered_in[1] - \
            (self.nb_tileY // 2) + (m_posY // TILE_SIZE) - 1
        return((m_posX, m_posY))

    def get_relative_tile_pos(self, X, Y):
        "Return the position of the tile on the screen (top left tile being 0,0)"
        relX = X - (self.centered_in[0] - (self.nb_tileX // 2) - 1)
        relY = Y - (self.centered_in[1] - (self.nb_tileY // 2) - 1)
        return (relX, relY)

    def is_valid_tile(self, numX, numY):
        """Return if a tile is a valid number on the map"""
        return ((0 <= numX < len(self.map[1])) and (0 <= numY < len(self.map)))

    def is_walkable_tile(self, numX, numY):
        "Return if a creature can walk the tile"
        return (self.is_valid_tile(numX, numY) and not self.map[numY][numX].wall)

    def get_free_tile(self):
        "Return a random walkable tile "
        X, Y = -1, -1
        while not self.is_walkable_tile(X, Y):
            X, Y = randint(0, len(self.map[0])), randint(0, len(self.map))
        return (X, Y)

    def simple_neigh(self, X, Y):
        """Return list of around tile, not minding void and wall"""
        return (('UL', (X - 1, Y - 1)), ('UR', (X + 1, Y - 1)),
                ('DL', (X - 1, Y + 1)), ('DR', (X + 1, Y + 1)),
                ('U', (X, Y - 1)), ('D', (X, Y + 1)),
                ('L', (X - 1, Y)), ('R', (X + 1, Y)))

    def neighbor_list(self, X, Y):
        """ Return list of accessible neighbors for tile (X,Y) and directions"""
        around = []
        corner_list = {'UL': (X - 1, Y - 1), 'UR': (X + 1, Y - 1),
                       'DL': (X - 1, Y + 1), 'DR': (X + 1, Y + 1)}
        side_list = {'U': (X, Y - 1), 'D': (X, Y + 1),
                     'L': (X - 1, Y), 'R': (X + 1, Y)}
        for action, tile in side_list.items():
            if self.is_walkable_tile(*tile):
                around.append((tile, action))

        # + tester si DL UL UR DR sont des murs
        if self.is_walkable_tile(side_list['U'][0], side_list['U'][1]):
            if self.is_walkable_tile(side_list['L'][0], side_list['L'][1]) \
                    and self.is_walkable_tile(corner_list['UL'][0], corner_list['UL'][1]):
                around.append((corner_list['UL'], 'UL'))
            if self.is_walkable_tile(side_list['R'][0], side_list['R'][1]) \
                    and self.is_walkable_tile(corner_list['UR'][0], corner_list['UR'][1]):
                around.append((corner_list['UR'], 'UR'))

        if self.is_walkable_tile(side_list['D'][0], side_list['D'][1]):
            if self.is_walkable_tile(side_list['L'][0], side_list['L'][1]) \
                    and self.is_walkable_tile(corner_list['DL'][0], corner_list['DL'][1]):
                around.append((corner_list['DL'], 'DL'))
            if self.is_walkable_tile(side_list['R'][0], side_list['R'][1]) \
                    and self.is_walkable_tile(corner_list['DR'][0], corner_list['DR'][1]):
                around.append((corner_list['DR'], 'DR'))
        return around


class MapObject:
    """A class of object on map"""

    def __init__(self, tile):
        self.tileX, self.tileY = tile

    def activable(self, player_posX, player_posY):
        """Return weather the player can activate the object or not"""
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
