"""This file contains the Game class which is the central element of
our game"""

import signal
import sys
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
        self.other_player = dict()  # key is the client id, value is a DistantPlayer instance
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
                    if event.button==3:
                        # Moving the player
                        dest = self.world_map.get_clicked_tile()
                        if self.world_map.is_walkable_tile(*dest):
                            self.player.update_path(dest)
                    if event.button==1:
                        # Using a chest
                        pX, pY = self.player.tileX, self.player.tileY
                        tileX, tileY = self.world_map.get_clicked_tile()
                        if  self.world_map.is_visible_tile(tileX, tileY) and \
                                self.world_map.local_chests[tileY][tileX] and \
                                self.world_map.local_chests[tileY][tileX].activable(pX, pY):
                            # Here give the loots
                            self.world_map.local_chests[tileY][tileX].use_chest(self.player)
                        if  self.world_map.is_visible_tile(tileX, tileY) and \
                                self.world_map.dist_chests[tileY][tileX] and \
                                self.world_map.dist_chests[tileY][tileX].activable(pX, pY):
                            # Here give the loots
                            self.request_chest((tileX, tileY))
                if event.type == pg.KEYDOWN:
                    # If we press tab, display the character status menu
                    if event.key == pg.K_TAB:
                        self.character_status.display = True
                    if event.key == pg.K_i:
                        self.player.inventory.display = True
                self.chat.event_handler(event)

                # Here we are checking inputs when the game is in the "playing" state

    def quit(self):
        """A function to properly quit the game"""
        self.running, self.playing = False, False
        self.current_menu.displaying = False
        self.client.disconnect()
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
        """Move the player p_id to the target pos on local game"""
        exX, exY = self.other_player[int(p_id)].get_current_pos()
        self.world_map.map[exY][exX].wall = False
        self.other_player[int(p_id)].move(*target)
        newX, newY = target
        self.world_map.map[newY][newX].wall = True

    def request_chest(self, pos):
        """Requests a distant chest on the map
        and sends a packet to the owner of the chest"""
        owner_id = self.world_map.dist_chests[pos[1]][pos[0]].owner_id
        owner_ip = ""
        try:
            for ip, id in self.player_id.items():
                if id==owner_id:
                    owner_ip = ip
        except:
            print("[Chests] Player not found in id list")
        else:
            # Building the packet 
            msg = str(self.own_id) + " 6 " + "request_" + str(pos[0]) + "/" + str(pos[1])
            msg += "_" + str(self.player.inventory.free_slots_number())
            self.network.send_message(msg, owner_ip)
            print("[Chests] You requested chest {0}/{1} from player [{2}]".format(pos[0], pos[1], owner_id))
