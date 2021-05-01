"""src/Item.py
This file contains all the classes related to the items : the different types of items, and their descriptions (which can be displayed in game by right clicking on the item)

Here is a quick overview of the class you're going to find here : 

Item --> The basis of every type of item, a sprite and a name
    CombatItem --> An item used for combat such as a weapon or an armor
    ConsumableItem --> Potions and herbs
    OresItem --> Currently useless in the game, but items that have a high gold value and for only purpose to be sold (if we add a merchant in the future)
ItemDesc --> The parent class of every item description
    CombatItemDesc --> Descriptions for the combat items
    ConsumableItemDesc --> Descriptions for the healing items, with a special button to use them
    OresItemDesc --> Descriptions for ores
"""
import pygame as pg
import pandas
from os import path
from src.interface import Text
from src.config.assets import fonts_folder, ingame_menus_folder

# Constants (to be moved ?)
CASCADIA_CODE = path.join(fonts_folder, "CascadiaCode.ttf")
CASCADIA_CODE_BOLD = path.join(fonts_folder, "CascadiaCodeBold.ttf")
DESC_TEXT_COLOR = "#2C2A27"


class Item():
    """Defines an item in the game, with a name, etc"""

    def __init__(self, name):
        # Initialization
        self.name = name

        # Position
        self.pos = (0, 0)
        self.item_sprite = None

        # Flag for description display
        self.display_desc = False

        # CSV Processing
        self.df = None


class CombatItem(Item):
    """Defines a specific item class for the combat items"""

    def __init__(self, name):
        Item.__init__(self, name)

        # Item data
        self.item_specs = {
            "name": name,
            "sp_class": None,
            "type": None,
            "cost": 0,
            "weight": 0,
            "bonus_def": 0,
            "bonus_dext": 0,
            "damages": None
        }

        self.item_from_csv(self.item_specs["name"])
        self.item_rect = self.item_sprite.get_rect()
        self.item_desc = CombatItemDesc(self)

    def item_from_csv(self, name):
        """Processes a CSV file containing data in order to create the item"""
        self.df = pandas.read_csv(
            'src/items_data/items_data.csv', skipinitialspace=True)

        # Getting back specs, sprite, etc
        self.item_sprite = pg.image.load(
            str(self.df[name].values[0])).convert_alpha()
        self.item_specs["sp_class"] = self.df[name].values[1]
        self.item_specs["type"] = self.df[name].values[2]
        self.item_specs["cost"] = self.df[name].values[3]
        self.item_specs["weight"] = self.df[name].values[4]
        # Specs depending on type of the item
        if self.item_specs["type"] == "weapon":
            self.item_specs["damages"] = self.df[name].values[5]
        elif self.item_specs["type"] == "armor":
            self.item_specs["bonus_def"] = self.df[name].values[5]
            self.item_specs["bonus_dext"] = self.df[name].values[6]
        elif self.item_specs["type"] == "shield":
            self.item_specs["bonus_def"] = self.df[name].values[5]


class ConsumableItem(Item):
    """Defines a specific item class for consumables items"""

    def __init__(self, name):
        Item.__init__(self, name)

        self.item_specs = {
            "name": name,
            "type": None,
            "cost": None,
            "weight": 0,
            "health_regen": 0
        }

        self.item_from_csv(self.item_specs["name"])
        self.item_rect = self.item_sprite.get_rect()
        self.item_desc = ConsumableItemDesc(self)

    def item_from_csv(self, name):
        """Processes a CSV file to create a consumable item"""
        self.df = pandas.read_csv(
            'src/items_data/consumables.csv', skipinitialspace=True)
        # Getting back data
        self.item_sprite = pg.image.load(
            str(self.df[name].values[0])).convert_alpha()
        self.item_specs["type"] = self.df[name].values[1]
        self.item_specs["weight"] = self.df[name].values[2]
        self.item_specs["cost"] = self.df[name].values[3]
        self.item_specs["health_regen"] = self.df[name].values[4]


class OresItem(Item):
    """Defines the different ores that a player can find, such as gold"""

    def __init__(self, name):
        Item.__init__(self, name)

        self.item_specs = {
            "name": name,
            "type": None,
            "weight": 0,
            "cost": 0,
        }

        self.item_from_csv(self.item_specs["name"])
        self.item_rect = self.item_sprite.get_rect()
        self.item_desc = OresItemDesc(self)

    def item_from_csv(self, name):
        """Processes a CSV file to create an ore item"""
        self.df = pandas.read_csv(
            'src/items_data/ores.csv', skipinitialspace=True)
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
        self.flag = False
        self.clock = pg.time.Clock()
        self.offset = 48
        self.x, self.y = None, None


class CombatItemDesc(ItemDesc):
    """Item descriptions for weapons and armor"""

    def __init__(self, item):
        ItemDesc.__init__(self, item)
        self.desc_sprite = pg.image.load(
            path.join(ingame_menus_folder, "desc_box.png"))
        self.surface = pg.Surface(self.desc_sprite.get_size())

        # CombatItemDesc generic informations
        self.info_text = [
            Text(self.surface, 8, 130, "This item can be used",
                 CASCADIA_CODE, "#383632", 13, False),
            Text(self.surface, 8, 140, "to fight ennemies",
                 CASCADIA_CODE, "#383632", 13, False)
        ]

        # Texts dictionnaries
        # Static is for the texts that wiill never move such as "Type : " and dynamic would be the values as "Weapon" or "40€"
        self.static_texts = {}
        self.dynamic_texts = {}

    def generate_item_properties(self):
        """This function retrieves the current item information in order to transform it in text"""
        # Name
        self.static_texts["name"] = Text(
            self.surface, self.surface.get_width() // 2, 22, self.item.name, CASCADIA_CODE, DESC_TEXT_COLOR, 16, True)

        # Type of the item
        self.static_texts["type"] = Text(
            self.surface, 8, 50, "Type : ", CASCADIA_CODE_BOLD, DESC_TEXT_COLOR, 14, False)
        self.dynamic_texts["type"] = Text(
            self.surface, 45, 50, self.item.item_specs["type"], CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)

        # Cost & Weight
        self.dynamic_texts["cost"] = Text(self.surface, 105, 175, str(
            self.item.item_specs["cost"]) + "$", CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
        self.dynamic_texts["weight"] = Text(self.surface, 8, 175, str(
            self.item.item_specs["weight"]) + "kg", CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)

        # Weapons/Armor/Shield stats
        if self.item.item_specs["type"] == "weapon":
            self.static_texts["damages"] = Text(
                self.surface, 8, 65, "Damages :", CASCADIA_CODE, 14, False)
            self.dynamic_texts["damages"] = Text(
                self.surface, 72, 65, self.item.item_specs["damages"], CASCADIA_CODE_BOLD, DESC_TEXT_COLOR, 14, False)
        elif self.item.item_specs["type"] == "armor":
            self.static_texts["bonus_def"] = Text(
                self.surface, 8, 65, "Bonus def. :", CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
            self.static_texts["bonus_dext"] = Text(
                self.surface, 8, 80, "Bonus dext. :", CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
            self.dynamic_texts["bonus_def"] = Text(self.surface, 85, 65, str(
                self.item.item_specs["bonus_def"]), CASCADIA_CODE_BOLD, DESC_TEXT_COLOR, 14, False)
            self.dynamic_texts["bonus_dext"] = Text(self.surface, 95, 80, str(
                self.item.item_specs["bonus_dext"]), CASCADIA_CODE_BOLD, DESC_TEXT_COLOR, 14, False)
        elif self.item.item_specs["type"] == "shield":
            self.static_texts["bonus_def"] = Text(
                self.surface, 8, 65, "Bonus def. :", CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
            self.dynamic_texts["bonus_def"] = Text(self.surface, 85, 65, str(
                self.item.item_specs["bonus_def"]), CASCADIA_CODE_BOLD, DESC_TEXT_COLOR, 14, False)

    def draw_desc(self):
        """Draws the description"""
        # Updating x/y
        self.x, self.y = self.item.item_rect.x + \
            self.offset, self.item.item_rect.y + self.offset
        self.surface.blit(self.desc_sprite, (0, 0))
        self.generate_item_properties()

        for key, value in self.static_texts.items():
            value.display_text()
        for key, value in self.dynamic_texts.items():
            value.display_text()
        self.info_text[0].display_text()
        self.info_text[1].display_text()

        for event in pg.event.get():
            # If we want to quit (quite unsure about them since it's not a clean closure of the game)
            if event.type == pg.QUIT:
                pg.display.quit()
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.item.display_desc = False


class ConsumableItemDesc(ItemDesc):
    """Descriptions for consumables items, with a button to use the consumable"""

    def __init__(self, item):
        ItemDesc.__init__(self, item)

        # The 2 different sprites
        self.desc_sprite = pg.image.load(
            path.join(ingame_menus_folder, "c_desc_box.png"))
        self.hover_desc_sprite = pg.image.load(
            path.join(ingame_menus_folder, "c_desc_box_hover.png"))
        self.current_sprite = self.desc_sprite
        self.surface = pg.Surface(self.current_sprite.get_size())

        # Setting up the click-box
        self.rect = self.surface.get_rect()
        self.x, self.y = self.item.item_rect.x + \
            self.offset, self.item.item_rect.y + self.offset
        self.rect.x, self.rect.y, self.rect.width, self.rect.height = self.x + \
            4, self.y + 159, 128, 25
        self.on_mouse = False

        # Info text
        self.info_text = [
            Text(self.surface, 8, 100, "This item can be used",
                 CASCADIA_CODE, DESC_TEXT_COLOR, 13, False),
            Text(self.surface, 8, 110, "to regenerate health",
                 CASCADIA_CODE, DESC_TEXT_COLOR, 13, False)
        ]
        # Texts dictionnaires : for more information refer to "CombatItemDesc" class
        self.static_texts = {}
        self.dynamic_texts = {}

    def generate_item_properties(self):
        """This functions creates the texts associated with our descriptions"""
        self.static_texts["name"] = Text(self.surface, self.surface.get_width(
        ) // 2, 22, self.item.name, CASCADIA_CODE, DESC_TEXT_COLOR, 16, True)
        # Type
        self.static_texts["type"] = Text(
            self.surface, 8, 50, "Type :", CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
        self.dynamic_texts["type"] = Text(self.surface, 45, 50, str(
            self.item.item_specs["type"]), CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
        # Cost & weight
        self.dynamic_texts["cost"] = Text(self.surface, 105, 145, str(
            self.item.item_specs["cost"]), CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
        self.dynamic_texts["weight"] = Text(self.surface, 8, 145, str(
            self.item.item_specs["weight"]), CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
        # Item healh regeneration
        self.static_texts["type"] = Text(
            self.surface, 8, 65, "Health Regen. :", CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)
        self.dynamic_texts["health_regen"] = Text(self.surface, 105, 65, str(
            self.item.item_specs["health_regen"]), CASCADIA_CODE, DESC_TEXT_COLOR, 14, False)

    def draw_desc(self):
        """Draws the description, and starts a loop to get the event 
        in case the user wants to use the item"""

        self.flag = False
        while True:

            # Updating x and y coords
            self.x, self.y = self.item.item_rect.x + \
                self.offset, self.item.item_rect.y + self.offset
            self.rect.x, self.rect.y, self.rect.width, self.rect.height = self.x + \
                4, self.y + 159, 128, 5

            for key, value in self.static_texts.items():
                value.display_text()
            for key, value in self.dynamic_texts.items():
                value.display_text()

            for event in pg.event.get():
                # If we want to quit (quite unsure about them since it's not a clean closure of the game)
                if event.type == pg.QUIT:
                    pg.display.quit()
                    pg.quit()
                # Hovering
                if event.type == pg.MOUSEMOTION:
                    self.on_mouse = True if self.rect.collidepoint(
                        event.pos) else False
                # On Click
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.item.display_desc = False
                        # TO FILL LATER
                    elif event.button == 1 and self.rect.collidepoint(event.pos):
                        self.add_health()
                    else:
                        self.item.display_desc = False
                # If a key is pressed
                if event.type == pg.KEYDOWN:
                    pass
                    # to fill


class OresItemDesc(ItemDesc):
    """The description class for ores"""

    def __init__(self, item):
        ItemDesc.__init__(self, item)
        pass
