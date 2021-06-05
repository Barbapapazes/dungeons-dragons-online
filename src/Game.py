"""This file contains the Game class which is the central element of
our game"""

import signal
import sys
import time
from os import path
import pygame as pg
from src.config.assets import menus_folder
from src.network import Client, Network
from src.Map import Map
from src.Player import Player
from src.Enemy import manage_enemy
from src.utils.network import enqueue_output
from .menu import MenuCharacter, MenuJoin, MenuMain
from src.config.window import RESOLUTION, TILE_SIZE
from src.config.colors import BLACK, WHITE
from src.UI import CharacterStatus, Chat


class Game:
    """The game class"""

    def __init__(self):

        # create a signal handler that will ignore SIGINT (CTRL + C) signals.
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        pg.init()
        pg.display.set_caption("Donjons & Python")
        pg.mouse.set_cursor(*pg.cursors.tri_left)
        self.clock = pg.time.Clock()

        self.running = True
        self.playing = False
        self.menu_running = True

        self.resolution = RESOLUTION
        self.window = pg.display.set_mode(self.resolution)

        # self.display is basically the canvas in which we blit everything
        self.display = pg.Surface(self.resolution)
        self.background = pg.transform.scale(
            pg.image.load(path.join(menus_folder, "background.png")),
            self.resolution,
        )
        self.display.blit(self.background, (0, 0))

        # -------MAP------- #
        self.world_map = Map("./src/maps/map1/map1.txt")
        # Chest list
        self.chest_list = []
        # ------PLAYER----- #
        self.player = Player(self)
        self.other_player = (
            dict()
        )  # key is the client id, value is a DistantPlayer instance
        # ------ENEMY------ #
        self.enemy_list = []
        # ------MENUS------ #
        self.main_menu = MenuMain(self)
        self.character_menu = MenuCharacter(self)
        self.join_menu = MenuJoin(self)
        self.current_menu = self.main_menu

        # ----INGAME MENUS---- #
        self.character_status = CharacterStatus(self)

        # ----CHAT---- #
        self.chat = Chat(400, 180, (15, 15), WHITE, 15, self)

        # ----NETWORK---- #
        self.player_id = dict()
        # Initialized when a party is created (10) or w<hen id is updated from other clients
        self.own_id = -1
        self.network = Network(self)
        self.client = Client(self)

    def check_events(self):
        "Checks for events in our game"
        for event in pg.event.get():

            if event.type == pg.QUIT:
                self.quit()
            if self.menu_running:
                self.current_menu.check_events(event)
            if self.playing:
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        ### --- INVENTORY HANDLING --- ###
                        if self.player.inventory.display:
                            self.handle_inventory_events(event)
                        else:
                            ### --- PLAYER MOVEMENT --- ###
                            dest = self.world_map.get_clicked_tile()
                            if self.world_map.is_walkable_tile(*dest):
                                self.player.update_path(dest)
                    if event.button == 1:
                        # Using a chest
                        pX, pY = self.player.tileX, self.player.tileY
                        tileX, tileY = self.world_map.get_clicked_tile()
                        if self.is_chest_clickable(
                            "local", (pX, pY), (tileX, tileY)
                        ):
                            # Here give the loots
                            self.world_map.local_chests[tileY][
                                tileX
                            ].use_chest(self.player)
                            self.send_update_chests((tileX, tileY))
                        if self.is_chest_clickable(
                            "dist", (pX, pY), (tileX, tileY)
                        ):
                            # Here give the loots
                            self.request_chest((tileX, tileY))
                if event.type == pg.KEYDOWN:
                    # If we press tab, display the character status menu
                    if event.key == pg.K_TAB:
                        self.character_status.display = (
                            not self.character_status.display
                        )
                    if event.key == pg.K_i:
                        self.player.inventory.display = (
                            not self.player.inventory.display
                        )
                self.chat.event_handler(event)
            # Inventory drag and drop
            if (
                not self.player.inventory.current_desc
                and self.player.inventory.display
            ):
                self.player.inventory.drag_and_drop(event)

                # Here we are checking inputs when the game is in the "playing" state

    def quit(self):
        """A function to properly quit the game"""
        print("[Game] Quiting game ...")
        self.running, self.playing = False, False
        self.current_menu.displaying = False
        try:
            self.network.send_chests_disconnect()
        except:
            print("Couldn't send chest on disconnection : nobody connected")
        time.sleep(0.5)
        self.client.disconnect()
        time.sleep(0.5)
        pg.quit()
        sys.exit()

    def update_screen(self):
        """Updates the whole screen by bliting self.display"""
        self.window.blit(self.display, (0, 0))
        pg.display.update()
        self.window.fill((0, 0, 0))

    def game_loop(self):
        """The loop of the game"""
        while self.playing:
            self.display.fill((0, 0, 0))
            self.world_map.draw(self.display)
            self.world_map.draw_mini(self.display)
            self.player.move()
            manage_enemy(self)
            self.player.draw(self.display)
            for o_player in self.other_player.values():
                o_player.draw(self.world_map, self.display)
            self.chat.draw(self.display)
            self.character_status.draw()
            self.player.inventory.draw()
            self.check_events()
            self.update_screen()
            self.clock.tick(30)
            self.network.server()

    def distant_player_move(self, p_id, target):
        """Moves a distant player on the map

        Args:
            p_id (str/int): the player ID
            target (tuple(int)): the position where he needs to move
        """
        try:
            exX, exY = self.other_player[int(p_id)].get_current_pos()
            self.world_map.map[exY][exX].wall = False
            self.other_player[int(p_id)].move(*target)
            newX, newY = target
            self.world_map.map[newY][newX].wall = True
        # This exception will be triggered when the player receives
        # his own movement, because when someone connects we send him
        #  every other movement of other players which he is in
        # I didn't find a way to make it easier and I think just ignoring
        #  when you get your own movement is a good way to proceed
        except KeyError:
            pass

    ### -- CHEST RELATED -- ###

    def request_chest(self, pos):
        """Sends a request to the player which owns
        the chest to get what's inside of it

        Args:
            pos (tuple(int)): the position of the chest
        """
        owner_id = self.world_map.dist_chests[pos[1]][pos[0]].owner_id
        owner_ip = ""
        try:
            for ip, id in self.player_id.items():
                if id == owner_id:
                    owner_ip = ip
        except:
            print("[Chests] Player not found in id list")
        else:
            # Building the packet
            msg = (
                str(self.own_id)
                + " 6 "
                + "request_"
                + str(pos[0])
                + "/"
                + str(pos[1])
            )
            msg += "_" + str(self.player.inventory.free_slots_number())
            self.network.send_message(msg, owner_ip)
            print(
                "[Chests] You requested chest {0}/{1} from player [{2}]".format(
                    pos[0], pos[1], owner_id
                )
            )

    def send_update_chests(self, pos):
        """Sends an update to other players when you
        open your own local chest

        Args:
            pos (tuple(int)): position of the chest
        """
        udpate_msg = (
            str(self.own_id)
            + " 6 "
            + "update"
            + "_"
            + str(pos[0])
            + "/"
            + str(pos[1])
        )
        self.network.send_global_message(udpate_msg)

    def is_chest_clickable(self, type, pos, tiles):
        """Verifies if a chest is clickable by testing
        if it exists/is in range/is empty...

        Args:
            type (str): either "local" or "dist" for the type of chest
            pos (tuple(int)): the position of the player
            tiles (tuple(int)): the tile on which the chest is

        Returns:
            [type]: [description]
        """

        tileX, tileY = tiles
        pX, pY = pos

        # Local chests
        if type == "local":
            return (
                self.world_map.is_visible_tile(tileX, tileY)
                and self.world_map.local_chests[tileY][tileX]
                and self.world_map.local_chests[tileY][tileX].activable(pX, pY)
                and not self.world_map.local_chests[tileY][tileX].is_opened
            )
        # Distant chests
        elif type == "dist":
            return (
                self.world_map.is_visible_tile(tileX, tileY)
                and self.world_map.dist_chests[tileY][tileX]
                and self.world_map.dist_chests[tileY][tileX].activable(pX, pY)
                and not self.world_map.dist_chests[tileY][tileX].is_opened
            )

    ### -- INVENTORY RELATED -- ###

    def handle_inventory_events(self, event):
        """Handles the events of the inventory (used
        to fix a bug that pauses the game)

        Args:
            event (pygame.Event): pygame event object
        """

        inventory = self.player.inventory
        item_on_mouse = None

        # Item taken in the inventory
        if inventory.detect_item_inv(*event.pos):
            item_on_mouse = inventory.inv_grid[inventory.gtoc_y(event.pos[1])][
                inventory.gtoc_x(event.pos[0])
            ]
        #  Item taken in the equipment
        elif inventory.detect_item_eq(*event.pos):
            item_on_mouse = inventory.equipment[inventory.gtoc_x(event.pos[0])]
        # If the item is already displaying a description we close it
        if item_on_mouse and item_on_mouse.display_desc:
            inventory.current_desc = None
            item_on_mouse.display_desc = False
        # Else we display his description
        elif item_on_mouse and not item_on_mouse.display_desc:
            inventory.current_desc = item_on_mouse.item_desc
            item_on_mouse.display_desc = True
        if event.type == pg.QUIT:
            self.quit()
