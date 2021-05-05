"""
src/Item.py

This file contains all the classes related to the items : the different types of items, and 
their descriptions (which can be displayed in game by right clicking on the item)
"""
import pygame as pg
import pandas
from os import path
from src.interface import Text
from src.config.assets import ingame_menus_folder, item_data_folder
from src.config.fonts import CASCADIA, CASCADIA_BOLD
from src.config.colors import DESC_TEXT_COLOR

# Constants 
NOT_CONS = 1 
QUIT_DESC = 2
USE_ITEM = 3
QUIT_GAME = 4


class Item():
    """Defines an item in the game : each item has specific properties that come from their data .CSV file
    """

    def __init__(self, name):
        # Initialization
        self.name = name

        # Position in the inventory
        self.pos = (0, 0)
        self.item_sprite = None

        # Flag for description display
        self.display_desc = False

        # Dataframe "df" (two dimensional array-like structure with data, see pandas doc for more informations)
        self.df = None


class CombatItem(Item):
    """Defines a specific item class for the combat items (swords, axes, armors)"""

    def __init__(self, name):
        super().__init__(name)

        # Item data
        self.item_specs = {
            "name": name,
            "sp_class": None,
            "type": None,
            "cost": 0,
            "weight": 0,
            "bonus_def": 0,
            "bonus_dext": 0,
            "damages": ""
        }

        # Filling item specs with the .CSV data file
        self.combat_item_from_csv(self.item_specs["name"])
        self.item_rect = self.item_sprite.get_rect()

        # Item description
        self.item_desc = CombatItemDesc(self)

    def combat_item_from_csv(self, name):
        """Processes a CSV file containing data in order to create the item"""
        self.df = pandas.read_csv(
            path.join(item_data_folder, 'items_data.csv'), skipinitialspace=True)

        # Getting back specs, sprite, etc
        self.item_sprite = pg.image.load(
            str(self.df[name].values[0])).convert_alpha()
        self.item_specs["sp_class"] = self.df[name].values[1]
        self.item_specs["type"] = self.df[name].values[2]
        self.item_specs["cost"] = int(self.df[name].values[3])
        self.item_specs["weight"] = int(self.df[name].values[4])

        # Specs depending on type of the item
        if self.item_specs["type"] == "weapon":
            self.item_specs["damages"] = str(self.df[name].values[5])
        elif self.item_specs["type"] == "armor":
            self.item_specs["bonus_def"] = int(self.df[name].values[5])
            self.item_specs["bonus_dext"] = int(self.df[name].values[6])
        elif self.item_specs["type"] == "shield":
            self.item_specs["bonus_def"] = int(self.df[name].values[5])


class ConsumableItem(Item):
    """Defines a specific item class for consumables items, currently
    with only healing purposes"""

    def __init__(self, name):
        super().__init__(name)

        self.item_specs = {
            "name": name,
            "type": None,
            "cost": None,
            "weight": 0,
            "health_regen": 0
        }

        # Retrieving item specs from the .CSV data file
        self.consumable_item_from_csv(self.item_specs["name"])
        self.item_rect = self.item_sprite.get_rect()

        # Consumable item description
        self.item_desc = ConsumableItemDesc(self)

    def consumable_item_from_csv(self, name):
        """Processes a CSV file to create a consumable item"""
        self.df = pandas.read_csv(
            path.join(item_data_folder,'consumables.csv'), skipinitialspace=True)
        # Getting back data
        self.item_sprite = pg.image.load(
            str(self.df[name].values[0])).convert_alpha()
        self.item_specs["type"] = self.df[name].values[1]
        self.item_specs["weight"] = self.df[name].values[2]
        self.item_specs["cost"] = self.df[name].values[3]
        self.item_specs["health_regen"] = self.df[name].values[4]


class OresItem(Item):
    """Defines the different ores that a player can find, such as gold
    They have currently no use in the game since merchant is not implemented"""

    def __init__(self, name):
        super().__init__(name)

        self.item_specs = {
            "name": name,
            "type": None,
            "weight": 0,
            "cost": 0,
        }

        # Retrieveing item data from .CSV
        self.ores_item_from_csv(self.item_specs["name"])
        self.item_rect = self.item_sprite.get_rect()

        # Item description for ores
        self.item_desc = OresItemDesc(self)

    def ores_item_from_csv(self, name):
        """Processes a CSV file to create an ore item"""
        self.df = pandas.read_csv(
            path.join(item_data_folder, 'ores.csv'), skipinitialspace=True)
        # Getting back data
        self.item_sprite = pg.image.load(
            str(self.df[name].values[0])).convert_alpha()
        self.item_specs["type"] = self.df[name].values[1]
        self.item_specs["weight"] = self.df[name].values[2]
        self.item_specs["cost"] = self.df[name].values[3]


class ItemDesc():
    """The parent class of every item description"""

    def __init__(self, item):
        self.item = item

        # Displaying purposes
        self.clock = pg.time.Clock()


class CombatItemDesc(ItemDesc):
    """Item descriptions for weapons and armor"""

    def __init__(self, item):
        # Parent class constructor
        super().__init__(item)

        # Graphical parts
        self.desc_sprite = pg.image.load(
            path.join(ingame_menus_folder, "desc_box.png"))
        self.surface = pg.Surface(self.desc_sprite.get_size())

        # CombatItemDesc generic informations
        self.info_text = [
            Text(self.surface, 14, 130, "This item is used",
                 CASCADIA, "#383632", 10, False),
            Text(self.surface, 14, 140, "to fight ennemies",
                 CASCADIA, "#383632", 10, False)
        ]

        # Texts dictionnaries
        # Static is for the texts that wiill never move such as "Type : " and dynamic texts would be the values as "Weapon" or "40€"
        self.static_texts = {}
        self.dynamic_texts = {}

    def generate_item_properties(self):
        """This function retrieves the current item information in order to transform it in text"""
        # Name
        self.static_texts["name"] = Text(
            self.surface, self.surface.get_width() // 2, 22, self.item.name, CASCADIA, DESC_TEXT_COLOR, 16, True)

        # Type of the item
        self.static_texts["type"] = Text(
            self.surface, 8, 50, "Type :", CASCADIA_BOLD, DESC_TEXT_COLOR, 12, False)
        self.dynamic_texts["type"] = Text(
            self.surface, 55, 50, self.item.item_specs["type"], CASCADIA, DESC_TEXT_COLOR, 12, False)

        # Cost & Weight
        self.dynamic_texts["cost"] = Text(self.surface, 100, 165, str(
            self.item.item_specs["cost"]) + "$", CASCADIA, DESC_TEXT_COLOR, 12, False)
        self.dynamic_texts["weight"] = Text(self.surface, 8, 165, str(
            self.item.item_specs["weight"]) + "kg", CASCADIA, DESC_TEXT_COLOR, 12, False)

        # Weapons/Armor/Shield stats
        if self.item.item_specs["type"] == "weapon":
            self.static_texts["damages"] = Text(
                self.surface, 8, 65, "Damages :", CASCADIA_BOLD, DESC_TEXT_COLOR, 12, False)
            self.dynamic_texts["damages"] = Text(
                self.surface, 75, 65, self.item.item_specs["damages"], CASCADIA, DESC_TEXT_COLOR, 12, False)
        elif self.item.item_specs["type"] == "armor":
            self.static_texts["bonus_def"] = Text(
                self.surface, 8, 65, "Bonus def. :", CASCADIA_BOLD, DESC_TEXT_COLOR, 12, False)
            self.static_texts["bonus_dext"] = Text(
                self.surface, 8, 80, "Bonus dext. :", CASCADIA_BOLD, DESC_TEXT_COLOR, 12, False)
            self.dynamic_texts["bonus_def"] = Text(self.surface, 115, 65, str(
                self.item.item_specs["bonus_def"]), CASCADIA, DESC_TEXT_COLOR, 12, False)
            self.dynamic_texts["bonus_dext"] = Text(self.surface, 115, 80, str(
                self.item.item_specs["bonus_dext"]), CASCADIA, DESC_TEXT_COLOR, 12, False)
        elif self.item.item_specs["type"] == "shield":
            self.static_texts["bonus_def"] = Text(
                self.surface, 8, 65, "Bonus def. :", CASCADIA, DESC_TEXT_COLOR, 12, False)
            self.dynamic_texts["bonus_def"] = Text(self.surface, 100, 65, str(
                self.item.item_specs["bonus_def"]), CASCADIA_BOLD, DESC_TEXT_COLOR, 12, False)

    def draw_desc(self):
        """Draws the description on the surface (returns 1 to differenciate if the description if the description
        of a combat item, consumable or ore)
        @return "NOT_CONS" to inform the inventory it's not a consumable item (with a value of 1)
        """

        # Bliting sprite
        self.surface.blit(self.desc_sprite, (0, 0))
        self.generate_item_properties()

        # Bliting texts
        for value in self.static_texts.values():
            value.display_text()
        for value in self.dynamic_texts.values():
            value.display_text()

        # Displaying generic information
        self.info_text[0].display_text()
        self.info_text[1].display_text()
        return NOT_CONS


class ConsumableItemDesc(ItemDesc):
    """Descriptions for consumables items, with a button to use the consumable
    """

    def __init__(self, item):
        # Parent constructor
        super().__init__(item)

        # The 2 different sprites
        self.desc_sprite = pg.image.load(
            path.join(ingame_menus_folder, "c_desc_box.png"))
        self.hover_desc_sprite = pg.image.load(
            path.join(ingame_menus_folder, "c_desc_box_hover.png"))
        self.current_sprite = self.desc_sprite
        self.surface = pg.Surface(self.current_sprite.get_size())
        self.rect = self.surface.get_rect()

        # Info text
        self.info_text = [
            Text(self.surface, 12, 100, "This item is used",
                 CASCADIA, "#383632", 10, False),
            Text(self.surface, 9, 110, "to regenerate health",
                 CASCADIA, "#383632", 10, False)
        ]
        # Texts dictionnaires : for more information refer to "CombatItemDesc" class
        self.static_texts = {}
        self.dynamic_texts = {}

    def generate_item_properties(self):
        """This functions creates the texts associated with our descriptions"""
        self.static_texts["name"] = Text(self.surface, self.surface.get_width(
        ) // 2, 22, self.item.name, CASCADIA, DESC_TEXT_COLOR, 16, True)

        # Type of the item
        self.static_texts["type"] = Text(
            self.surface, 8, 50, "Type :", CASCADIA_BOLD, DESC_TEXT_COLOR, 12, False)
        self.dynamic_texts["type"] = Text(
            self.surface, 50, 50, self.item.item_specs["type"], CASCADIA, DESC_TEXT_COLOR, 12, False)

        # Cost & Weight
        self.dynamic_texts["cost"] = Text(self.surface, 100, 137, str(
            self.item.item_specs["cost"]) + "$", CASCADIA, DESC_TEXT_COLOR, 12, False)
        self.dynamic_texts["weight"] = Text(self.surface, 8, 137, str(
            self.item.item_specs["weight"]) + "kg", CASCADIA, DESC_TEXT_COLOR, 12, False)

        # Item healh regeneration
        self.static_texts["health_regen"] = Text(
            self.surface, 8, 65, "Health Regen. :", CASCADIA_BOLD, DESC_TEXT_COLOR, 12, False)
        self.dynamic_texts["health_regen"] = Text(self.surface, 118, 65, str(
            self.item.item_specs["health_regen"]), CASCADIA, DESC_TEXT_COLOR, 12, False)

    def draw_desc(self):
        """Draws the description, and starts a loop to get the event
        in case the user wants to use the item. Multiple return values because this 
        description is interactive and uses a "for event in..." pygame loop
        @return USE_ITEM if the user uses the item (value = 3)
                QUIT_DESC if the user quits the description
                QUIT_GAME if the user quits the game 
        
        """

        # Bliting background and generating item properties
        self.surface.blit(self.current_sprite, (0, 0))
        self.generate_item_properties()

        for value in self.static_texts.values():
            value.display_text()
        for value in self.dynamic_texts.values():
            value.display_text()

        self.info_text[0].display_text()
        self.info_text[1].display_text()

        for event in pg.event.get():
            # If the user has his mouse over the button, it changes color
            if event.type == pg.MOUSEMOTION:
                self.current_sprite = self.hover_desc_sprite if self.rect.collidepoint(
                    event.pos) else self.desc_sprite
            # If the user clicks on the button, it heals the player, otherwise quits the descriptions
            # For more precisions, see Inventory.draw_desc()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.item.display_desc = False
                if self.rect.collidepoint(event.pos):
                    return USE_ITEM  # Uses the potion (see Inventory.draw_desc())
                else:
                    # Quits the description (see Invnetory.draw_desc())
                    return QUIT_DESC
            if event.type == pg.QUIT:
                return QUIT_GAME


class OresItemDesc(ItemDesc):
    """The description class for ores"""

    def __init__(self, item):
        # Parent constructor
        super().__init__(item)

        self.desc_sprite = pg.image.load(
            path.join(ingame_menus_folder, "ore_desc_box.png"))
        self.surface = pg.Surface(self.desc_sprite.get_size())

        # CombatItemDesc generic informations
        self.info_text = [
            Text(self.surface, 18, 130, "This item has a",
                 CASCADIA, "#383632", 10, False),
            Text(self.surface, 17, 140, "great sell value",
                 CASCADIA, "#383632", 10, False)
        ]

        # Texts dictionnaries
        # Static is for the texts that wiill never move such as "Type : " and dynamic would be the values as "Weapon" or "40€"
        self.static_texts = {}
        self.dynamic_texts = {}

    def generate_item_properties(self):
        """This function retrieves the current item information in order to transform it in text"""
        # Name
        self.static_texts["name"] = Text(
            self.surface, self.surface.get_width() // 2, 22, self.item.name, CASCADIA_BOLD, DESC_TEXT_COLOR, 16, True)

        # Type of the item
        self.static_texts["type"] = Text(
            self.surface, 8, 50, "Type :", CASCADIA_BOLD, DESC_TEXT_COLOR, 12, False)
        self.dynamic_texts["type"] = Text(
            self.surface, 55, 50, self.item.item_specs["type"], CASCADIA, DESC_TEXT_COLOR, 12, False)

        # Cost & Weight
        self.dynamic_texts["cost"] = Text(self.surface, 100, 165, str(
            self.item.item_specs["cost"]) + "$", CASCADIA, DESC_TEXT_COLOR, 12, False)
        self.dynamic_texts["weight"] = Text(self.surface, 8, 165, str(
            self.item.item_specs["weight"]) + "kg", CASCADIA, DESC_TEXT_COLOR, 12, False)

    def draw_desc(self):
        """Draws the description"""
        # Bliting the sprite and generating text
        self.surface.blit(self.desc_sprite, (0, 0))
        self.generate_item_properties()

        for value in self.static_texts.items():
            value.display_text()
        for value in self.dynamic_texts.items():
            value.display_text()

        self.info_text[0].display_text()
        self.info_text[1].display_text()
        return 1
