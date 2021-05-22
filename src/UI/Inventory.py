""" 
src/UI/Inventory.py 

This class contains the fully working inventory separated in two parts :
    - The inventory
    - The equipment which influes on the statistics of the player

Items can be dragged and dropped, equipped, or put in the trash
"""
import pygame as pg
from src.config.assets import ingame_menus_folder
from os import path
from src.config.window import RESOLUTION
from src.interface import Text


class Inventory():
    """An inventory class with an inventory that contains the equipment and
    items of the character"""

    def __init__(self, game):
        self.game = game

        # Background
        self.background_sprite = pg.image.load(
            path.join(ingame_menus_folder, "inventory.png")).convert_alpha()

        # Surfaces
        self.surface = pg.Surface(self.background_sprite.get_size())
        self.surface.set_colorkey((0, 255, 0))
        self.bis = None
        self.bis_blurred = None
        # The following constants represent the width/height of the different
        # parts of the inventory on the sprite
        self.INV_WIDTH, self.INV_HEIGHT = (0, 324), (19, 279)
        self.EQ_WIDTH, self.EQ_HEIGHT = (0, 260), (323, 390)

        # Useful flags
        self.display = False
        self.clock = pg.time.Clock()

        # Position on screen
        self.screen_position = RESOLUTION[0] // 2 - self.surface.get_width(
        ) // 2, RESOLUTION[1] // 2 - self.surface.get_height() // 2

        # Inventory and equipment
        self.inv_grid = [[None] * 5 for _ in range(4)]
        self.equipment = [None, None, None, None]

        # Drag and drop purposes
        self.drag = False
        self.off_x, self.off_y = 0, 0  # offset for cosmetic purposes
        self.current_item = None  # item being dragged
        self.current_desc = None
        # Origin of the item being dragged (origin[0]=0 --> comes from the inventory,
        # origin[0]=1 --> comes from the equipment and following values are position)
        self.origin = None

    def draw(self):
        """Displays the inventory of the player"""
        # Blurring background
        if self.display:
            self.bis_blurred = self.game.display.copy()
            self.bis_blurred = self.blur_surface(self.bis_blurred)

        while self.display:

            # Blitting the background
            self.bis = self.bis_blurred.copy()
            self.surface.fill((0, 255, 0))
            self.surface.blit(self.background_sprite, (0, 0))

            # Bliting each item present in the inventory
            self.draw_items()
            self.bis.blit(self.surface, self.screen_position)
            self.draw_item_cursor()
            self.draw_item_desc()

            for event in pg.event.get():
                # Quitting the game
                if event.type == pg.QUIT:
                    self.display = False
                    self.game.quit()
                # If a key is pressed
                if event.type == pg.KEYDOWN:
                    # Inventory key
                    if event.key == pg.K_i:
                        self.close_inventory()
                # Handling descriptions
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 3 and not self.drag:
                    if self.detect_item_inv(*event.pos):
                        item_on_mouse = self.inv_grid[self.gtoc_y(
                            event.pos[1])][self.gtoc_x(event.pos[0])]
                    elif self.detect_item_eq(*event.pos):
                        item_on_mouse = self.equipment[self.gtoc_x(
                            event.pos[0])]
                    # If the item is already displaying a description we close it
                    if item_on_mouse.display_desc:
                        self.current_desc = None
                        item_on_mouse.display_desc = False
                    # Else we display his description
                    else:
                        self.current_desc = item_on_mouse.item_desc
                        item_on_mouse.display_desc = True
                # Drag and drop handling
                if not self.current_desc:
                    self.drag_and_drop(event)

            # Bliting the inventory scene to the game
            self.game.window.blit(self.bis, (0, 0))
            pg.display.update()
            self.clock.tick(70)

    def drag_and_drop(self, event):
        """Handles the drag and drop in the inventory
        This function is basically very complicated a needs simplifications for it in the future"""
        ### -------- IF AN ITEM IS CLICKED -------- ###
        if event.type == pg.MOUSEBUTTONDOWN and not event.type == pg.MOUSEBUTTONUP and not event.type == pg.MOUSEMOTION and event.button == 1:
            mx, my = event.pos
            # If the item is in the inventory
            if self.gtos_x(mx) in range(*self.INV_WIDTH) and self.gtos_y(my) in range(*self.INV_HEIGHT):
                # Getting back which item are we dragging and starting drag and drop
                if self.detect_item_inv(mx, my):
                    self.current_item = self.inv_grid[self.gtoc_y(
                        my)][self.gtoc_x(mx)]
                    self.origin = [0, self.gtoc_x(mx), self.gtoc_y(my)]
                    self.inv_grid[self.gtoc_y(my)][self.gtoc_x(mx)] = None

            # If the item is in the equipment
            if self.gtos_x(mx) in range(*self.EQ_WIDTH) and self.gtos_y(my) in range(*self.EQ_HEIGHT):
                if self.equipment[self.gtoc_x(mx)]:
                    self.current_item = self.equipment[self.gtoc_x(mx)]
                    self.origin = [1, self.gtoc_x(mx), 0]
                    self.equipment[self.gtoc_x(mx)] = None

            if self.current_item: 
                # Starting drag and drop
                self.drag = True
                # Calculating new coords for our item
                self.current_item.item_rect.x = mx - \
                    self.screen_position[0] - \
                    self.current_item.item_rect.width // 2
                self.current_item.item_rect.y = my - \
                    self.screen_position[1] - \
                    self.current_item.item_rect.height // 2
                # Displaying item on cursor when it's clicked
                self.draw_item_cursor()
        ### -------- IF AN ITEM IS RELEASED -------- ###
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.drag = False
            mx, my = event.pos
            # If the item is released anywhere but not in inventory
            if self.current_item and not (self.gtos_x(mx) in range(*self.INV_WIDTH) and self.gtos_y(my) in range(*self.INV_HEIGHT)) \
                    and not (self.gtos_x(mx) in range(*self.EQ_WIDTH) and self.gtos_y(my) in range(*self.EQ_HEIGHT)):
                # If the item comes from the inventory
                if self.origin[0] == 0:
                    self.current_item.pos = self.origin[1], self.origin[2]
                    self.inv_grid[self.origin[2]
                                  ][self.origin[1]] = self.current_item
                else:  #  If the item comes from the equipment
                    self.current_item.pos = self.origin[1], self.origin[2]
                    self.equipment[self.origin[1]] = self.current_item

            # If the item is released in the inventory
            if self.current_item and self.gtos_x(mx) in range(*self.INV_WIDTH) and self.gtos_y(my) in range(*self.INV_HEIGHT):
                # If there is an item in the inventory case we are trying to release in
                if self.detect_item_inv(mx, my):
                    # If the item we want to put comes from the inventory
                    if self.origin[0] == 0:
                        self.inv_grid[self.gtoc_y(my)][self.gtoc_x(
                            mx)].pos = self.origin[1], self.origin[2]
                        self.inv_grid[self.origin[2]][self.origin[1]] = self.inv_grid[self.gtoc_y(
                            my)][self.gtoc_x(mx)]
                    else:
                        self.inv_grid[self.gtoc_y(my)][self.gtoc_x(
                            mx)].pos = self.origin[1], 0
                        self.equipment[self.origin[1]] = self.inv_grid[self.gtoc_y(
                            my)][self.gtoc_x(mx)]
                self.current_item.pos = self.gtoc_x(mx), self.gtoc_y(my)
                self.inv_grid[self.gtoc_y(my)][self.gtoc_x(
                    mx)] = self.current_item
                # If the item is released in the trash
                if self.gtoc_x(mx) == 4 and self.gtoc_y(my) == 3:
                    self.inv_grid[self.gtoc_y(my)][self.gtoc_x(mx)] = None

            # If the item is released in the equipment
            if self.current_item and self.gtos_x(mx) in range(*self.EQ_WIDTH) and self.gtos_y(my) in range(*self.EQ_HEIGHT):
                # If there is an item in the equipment case we are trying to release in
                if self.equipment[self.gtoc_x(mx)]:
                    # If the item comes from the inventory
                    if self.origin[0] == 0:
                        self.equipment[self.gtoc_x(
                            mx)].pos = self.origin[1], self.origin[2]
                        self.inv_grid[self.origin[2]][self.origin[1]
                                                      ] = self.equipment[self.gtoc_x(mx)]
                    else:
                        self.equipment[self.gtoc_x(mx)].pos = self.origin[1], 0
                        self.equipment[self.origin[1]
                                       ] = self.equipment[self.gtoc_x(mx)]
                self.current_item.pos = self.gtoc_x(mx), 0
                self.equipment[self.gtoc_x(mx)] = self.current_item
            self.current_item, self.origin = None, None
        ### -------- IF AN ITEM IS BEING DRAGGED -------- ###
        elif event.type == pg.MOUSEMOTION:
            mx, my = event.pos
            if self.drag and self.current_item:
                # Calculating new coords for our item
                self.current_item.item_rect.x = mx - \
                    self.screen_position[0] - \
                    self.current_item.item_rect.width // 2
                self.current_item.item_rect.y = my - \
                    self.screen_position[1] - \
                    self.current_item.item_rect.height // 2
                # Display item on cursor
                self.draw_item_cursor()

    def draw_item_cursor(self):
        """Draws an item on the cursor when it's dragged"""
        if self.current_item:
            self.surface.blit(self.current_item.item_sprite,
                              (self.current_item.item_rect.x, self.current_item.item_rect.y))
            self.bis.blit(self.surface, self.screen_position)

    def draw_items(self):
        """Draws the items in the inventory and equipment"""
        # Drawing each item in inventory
        [self.surface.blit(item.item_sprite, (4 + item.pos[0] * 64, 23 + item.pos[1] * 64))
         for sublist in self.inv_grid for item in sublist if item is not None]
        # Drawing each item in the equipment
        [self.surface.blit(item.item_sprite, (4 + item.pos[0] * 64, 327))
         for item in self.equipment if item is not None]

    def draw_item_desc(self):
        """Draws the current item desc"""
        # If we currently have an item description to display
        if self.current_desc:
            # Recentre the rectangle of the consumables
            # I don't do it in Item.py to avoid circular import on src.config.wiindow in the futre
            # It's not clean and I'm aware of it
            if self.current_desc.item.item_specs["type"] == "Consumable":
                self.current_desc.rect.x = self.screen_position[0] + \
                    self.surface.get_width() + 34
                self.current_desc.rect.y = self.screen_position[1] + \
                    self.surface.get_height() // 6 + 159
                self.current_desc.rect.width, self.current_desc.rect.height = 128, 25
            # Before the next "if" statement because can't blit a none object
            self.bis.blit(self.current_desc.surface,
                          (self.screen_position[0] + self.surface.get_width()
                           + 30, self.screen_position[1] + self.surface.get_height() // 6))
            # Every "draw_desc()" method returns 1 except the one for the consumables because they
            # have a button to consume the item : they return 2 when we click out of the button to
            # close the description
            if self.current_desc.draw_desc() == 2:
                self.current_desc = None
            elif self.current_desc.draw_desc() == 3:
                self.use_consumable()
            elif self.current_desc.draw_desc() == 4:
                self.game.quit()

    def last_position(self):
        """Finds the first position in the inventory where there is not item
        Example : if there are 2 items in the 2 first slots of the inventory,
        this function returns 2 as inv_grid[2] is the first empty spot
        """
        row, column = 0, 0
        for row in range(len(self.inv_grid)):
            for column in range(len(self.inv_grid[row])):
                if not self.inv_grid[row][column]:
                    return (column, row)

    def is_full(self):
        """Returns true if the inventory is full"""
        count = 0
        for sublist in self.inv_grid:
            for item in sublist:
                if item:
                    count += 1
        return count == 19

    def add_items(self, items):
        """Adds a list of items in the inventory"""
        for item in items:
            if not self.is_full():
                (x, y) = self.last_position()
                item.pos = (x, y)
                self.inv_grid[y][x] = item
            else:
                print(
                    f"[Inventory.add_items()] : Impossible to add item {item} because inventory is full")

    def blur_surface(self, surface):
        """Blurs the "bis blurred" display"""
        for i in range(1, 4):
            surface = pg.transform.smoothscale(
                surface, (RESOLUTION[0] * i, RESOLUTION[1] * i))
            surface = pg.transform.smoothscale(
                surface, (RESOLUTION[0] // i * 2, RESOLUTION[1] // i * 2))
            surface = pg.transform.smoothscale(surface, RESOLUTION)
        return surface

    def close_inventory(self):
        """Closes the inventory by setting flags to false"""
        self.drag = False
        self.display = False

    def detect_item_inv(self, mx, my):
        """Detects if there is an item under the mouse in the inventory"""
        if self.gtos_x(mx) in range(*self.INV_WIDTH) and self.gtos_y(my) in range(*self.INV_HEIGHT):
            return self.inv_grid[self.gtoc_y(my)][self.gtoc_x(mx)] is not None

    def detect_item_eq(self, mx, my):
        """Detects if there is an item under the mouse in the equipment"""
        if self.gtos_x(mx) in range(*self.EQ_WIDTH) and self.gtos_y(my) in range(*self.EQ_HEIGHT):
            return self.equipment[self.gtoc_x(mx)] is not None

    def use_consumable(self):
        """This functions is called whenever the player uses a consumable item :
        it first adds health to the player and then deletes the item"""
        self.game.player.health += int(
            self.current_desc.item.item_specs["health_regen"])

        # Verifying if we don't add too much health
        if self.game.player.health > self.game.player.max_value["health"]:
            self.game.player.health = self.game.player.max_value["health"]
        # Deleting the consumable
        self.inv_grid[self.current_desc.item.pos[1]
                      ][self.current_desc.item.pos[0]] = None
        del self.current_desc.item
        self.current_desc = None

    def get_equipment_stats(self):
        """Returns a dictionnary with the bonus stats given by
        the current items equipped"""
        eq_stats = {
            "damages": "0d0",
            "dexterity": 0,
            "defense": 0
        }
        for item in self.equipment:
            if item:
                if item.item_specs["type"] == "weapon" and ((int(item.item_specs["damages"][2]) * int(item.item_specs["damages"][0]) > int(eq_stats["damages"][2]) * int(eq_stats["damages"][0]))
                                                            or (int(item.item_specs["damages"][2]) * int(item.item_specs["damages"][0]) == int(eq_stats["damages"][2]) * int(eq_stats["damages"][0])
                                                                and int(item.item_specs["damages"][0]) > int(eq_stats["damages"][0]))):
                    eq_stats["damages"] = str(item.item_specs["damages"])
                elif item.item_specs["type"] == "armor":
                    eq_stats["dexterity"] += int(item.item_specs["bonus_dext"])
                    eq_stats["defense"] += int(item.item_specs["bonus_def"])
                elif item.item_specs["type"] == "shield":
                    eq_stats["defense"] += item.item_specs["bonus_def"]
        return eq_stats

    def get_weight(self):
        """Returns the weight of the inventory (money not in the count)"""
        weight = 0
        for sublist in self.inv_grid:
            for item in sublist:
                if item:
                    weight += int(item.item_specs["weight"])
        for item in self.equipment:
            if item:
                weight += int(item.item_specs["weight"])
        return weight
    
    def free_slots_number(self):
        """Returns the number of free slots in the inventory"""
        count = 0 
        for sublist in self.inv_grid:
            for item in sublist:
                if not item:
                    count += 1
        return count 

    # These functions are conversions functions : they are used to go from global mouse coords
    # to surface mouse coords (since the inventory has his own surface), global coords to case
    # of the inventory or even surface to case coords

    def gtos_x(self, x):
        """GLOBAL coord --> SURFACE coord"""
        return x - self.screen_position[0]

    def gtos_y(self, y):
        """GLOBAL coord --> SURFACE coord"""
        return y - self.screen_position[1]

    def stoc_x(self, x):
        """SURFACE coord --> CASE coord"""
        return (x - 4) // 64

    def stoc_y(self, y):
        """SURFACE coord --> CASE coord"""
        return (y - 23) // 64

    def gtoc_x(self, x):
        """GLOBAL coord --> CASE coord"""
        return self.stoc_x(self.gtos_x(x))

    def gtoc_y(self, y):
        """GLOBAL coord --> CASE coord"""
        return self.stoc_y(self.gtos_y(y))
