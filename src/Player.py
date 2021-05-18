from src.config.window import RESOLUTION, TILE_SIZE
from src.utils.astar import bfs
from src.utils.network import is_initialized_id
from src.UI.Inventory import Inventory
from src.interface import Text
from src.config.colors import WHITE
from src.config.fonts import CASCADIA_BOLD
from random import randint
import pygame as pg
from os import path
from .Item import CombatItem, ConsumableItem, OresItem


class Player:
    """The player class"""

    def __init__(self, game):
        self.game = game
        self.map = self.game.world_map
        self.image = pg.image.load("src/assets/player.png").convert_alpha()

        # Surface with a 25 pixels offset for the nickname 
        self.surface = pg.Surface(RESOLUTION)
        self.surface.set_colorkey((0,0,0))
        self.surface.blit(self.image, (RESOLUTION[0] // 2, RESOLUTION[1] //2))

        self.tileX = 2  # Will have to put map start point here
        self.tileY = 2
        self.futur_steps = []  # Will contain list of tile to go trough

        # Player base stats
        self.base_stats = {
            "strength": 3,
            "intelligence": 3,
            "dexterity": 3,
            "charisma": 3,
            "constitution": 3,
            "wisdom": 3
        }
        self.stats = {key: 0 for key in self.base_stats.keys()}
        
        self.max_value = {
            "health": 100
        }

        self.health = self.max_value["health"]
        self.defense = 0  # for combats
        self.damages = ""  # for damages
        self.money = 100

        # Inventory and items
        self.inventory = Inventory(self.game)
        axe = CombatItem("Axe")
        sword = CombatItem("Sword")
        armor = CombatItem("Plate Armor")
        small_potion = ConsumableItem("Small Potion")
        gold = OresItem("Gold Ore")
        shield = CombatItem("Wooden Shield")
        self.inventory.add_items(
            [axe, sword, small_potion, armor, gold, shield])

        # Nickname in game
        self.nickname = ""  # the actual nickname
        self.nickname_text = None  # The Text object displayed in game

    def draw(self, display):
        """Draw the player on the display"""
        s_width, s_height = RESOLUTION
        display.blit(self.image, (s_width // 2, s_height // 2))

    def take_damage(self, damage):
        """Give damage to player"""
        self.health -= damage

    def restore_health(self, min_restoration=0):
        """Restore player health, with a minimum of min_restoration"""
        self.health = self.health + randint(
            min_restoration, self.max_value["health"] - self.health)

    def move(self):
        """Move the player to X,Y (counted in tiles)"""
        if len(self.futur_steps) != 0:
            self.tileX, self.tileY = self.futur_steps.pop(0)
            # local move
            self.map.centered_in = [self.tileX, self.tileY]
            # Send move to other clients
            line = str(self.game.own_id) + " 4 " + \
                str(self.tileX) + "/" + str(self.tileY)
            if is_initialized_id(self.game.own_id):
                self.game.network.send_global_message(line)

    def get_current_pos(self):
        "Return X, Y the current position"
        return (self.tileX, self.tileY)

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
        direction_list = bfs((lastX, lastY), dest, self.map)
        for action in direction_list:
            step = (lastX + act_sum[action][0], lastY + act_sum[action][1])
            lastX, lastY = step
            self.futur_steps.append(step)

    def set_nickname(self, nickname):
        """Sets the nickname of the player and update the nickname 
    texts displayed in game"""
        self.nickname = nickname
        self.nickname_text = Text(
            self.surface, RESOLUTION[0]//2 + self.image.get_width()//2, RESOLUTION[1] //2 , self.nickname, CASCADIA_BOLD, WHITE, 15, True)
        self.nickname_text.display_text()

    def update_stats(self):
        """To update stats we need to get the equipment stats and add them to base stats"""
        # Getting back equipment stats
        eq_stats = self.inventory.get_equipment_stats()
        # Updating defense and damages
        self.defense = eq_stats["defense"]
        self.damages = eq_stats["damages"]
        # To calculate the current stats we first get back the base stats
        for key, value in self.base_stats.items():
            self.stats[key] = value
        # Adding items stats
        self.stats["dexterity"] += eq_stats["dexterity"]
        
class DistantPlayer:
    def __init__(self):
        self.image = pg.image.load("src/assets/extern_player.png")
        self.tileX = 2  # Will have to put map start point here
        self.tileY = 2
        self.stats = {
            "strength": 0,
            "intelligence": 0,
            "dexterity": 0,
            "charisma": 0,
            "constitution": 0,
            "wisdom": 0
        }

    def draw(self, map, display):
        """Draw the player on the display"""
        if map.is_visible_tile(self.tileX, self.tileY):
            relativX, relativY = map.get_relative_tile_pos(
                self.tileX, self.tileY)
            relativX, relativY = relativX * TILE_SIZE, relativY * TILE_SIZE
            display.blit(self.image, (relativX, relativY))

    def get_current_pos(self):
        "Return X, Y the current position"
        return (self.tileX, self.tileY)

    def move(self, X, Y):
        self.tileX = X
        self.tileY = Y
    
