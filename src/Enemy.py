from src.config.window import TILE_SIZE
from src.utils.astar import bfs
from random import randint
import pygame as pg


class Enemy:
    def __init__(self, map, e_id):
        self.id = e_id
        self.map = map
        self.image = None
        self.tileX, self.tileY = None, None

    def draw(self, display):
        """Draw the ennmy on the display"""
        if self.map.is_visible_tile(self.tileX, self.tileY):
            relativX, relativY = self.map.get_relative_tile_pos(
                self.tileX, self.tileY)
            relativX, relativY = relativX * TILE_SIZE, relativY * TILE_SIZE
            display.blit(self.image, (relativX, relativY))

    def get_pos(self):
        return(self.tileX, self.tileY)

    def walk(self, pos):
        #Ex tile is now free
        self.map.map[self.tileY][self.tileX].wall=False
        self.tileX, self.tileY = pos
        #New pos is occupied
        self.map.map[self.tileY][self.tileX].wall=True


class local_Enemy(Enemy):
    def __init__(self, map, e_id):
        super().__init__(map, e_id)
        self.tileX, self.tileY = self.map.get_free_tile()
        self.image = pg.image.load("src/assets/local_enemy.png")
        self.pause_turn = 1  # Pause the enemy during X turn
        self.futur_steps = []  # Will contain list of tile to go trough
        self.stats = {
            "strength": 0,
            "intelligence": 0,
            "dexterity": 0,
            "charisma": 0,
            "constitution": 0,
            "wisdom": 0
        }

        self.max_value = {
            "health": 70
        }

        self.health = self.max_value["health"]
    
    def is_in_range(self, pos):
        return (-2 < pos[0]-self.tileX < 2) and (-2 < pos[1]-self.tileY < 2)

    def detect(self, local_Player, distant_Player):
        """Detect if a player is in range to be attacked"""
        if self.is_in_range(local_Player.get_current_pos()):
            #Here you attack the player
            pass
        for d_player in distant_Player:
            if self.is_in_range(d_player.get_current_pos()):
                #Here as well (d_player.id to have the id then use it with game dict for the ip)
                pass

    def act(self, network):
        """Update position, wait or generate a path """
        if randint(0, 15) > 0:
            # We do not act 4 times out of 15
            return
        if len(self.futur_steps) != 0:
            # If we have a path; we continue to go through, except if it's a wall
            next_step = self.futur_steps.pop(0)
            if (self.map.is_walkable_tile(*next_step)):
                self.walk(next_step)
                network.send_enemy_update(self.id, self.get_pos())
            else:
                #If the path is no more valid
                self.update_path(self.random_dest())
        else:
            # The path is empty
            if self.pause_turn == 0:
                # If we already waited enough we generate a path
                self.update_path(self.random_dest())
                # And we prepare the number of pauses for when the path will be empty
                self.pause_turn = randint(2, 20)

            else:
                # We do nothing if we still need to wait
                self.pause_turn -= 1

    def take_damage(self, damage):
        """Give damage to local enemy"""
        self.health -= max(0, damage)
        if self.health > 0:
            return True
            # Send new health to all other player
        # Notify all the player that monster is dead
        return False

    def random_dest(self):
        "Find a random tile to go next"
        t_range = 8
        nextX = randint(max(0, self.tileX - t_range),
                        min(self.tileX + t_range, len(self.map.map[1])))
        nextY = randint(max(0, self.tileX - t_range),
                        min(self.tileX + t_range, len(self.map.map)))
        if not self.map.is_walkable_tile(nextX, nextY):
            return self.random_dest()
        else:
            return (nextX, nextY)

    def update_path(self, dest):
        "Create a path to destination"
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


class distant_Enemy(Enemy):
    def __init__(self, map, e_id, pos):
        super().__init__(map, e_id)
        self.tileX, self.tileY = pos
        self.map.map[self.tileY][self.tileX].wall=True
        self.image = pg.image.load("src/assets/distant_enemy.png")

    def take_damage(self, damage):
        """Give damage to enemy"""
        # Send to owner the damage
        pass


def manage_enemy(game):
    "Manage and create the enemy list"
    # --- LOCAL ENEMIES --- #
    # Try to create a new enemy
    if game.own_id < 0:
        # The connection is being established so we wait
        return
    if (len(game.local_enemy_list) < 5) and (randint(0, 20) > 19):
        e_id = len(game.local_enemy_list)
        while (any(e.id == e_id for e in game.local_enemy_list)):
            e_id += 1
        new_e = local_Enemy(game.world_map, e_id)
        game.network.send_enemy_update(
            new_e.id, new_e.get_pos(), isNewEnemy=True)
        game.local_enemy_list.append(new_e)

    for e in game.local_enemy_list:
        e.detect(game.player, game.other_player.values())
        e.act(game.network)
        e.draw(game.display)
    # --- DISTANT ENEMIES --- #
    for e_list in game.distant_enemy_list.values():
        for e in e_list:
            e.draw(game.display)


def find_enemy_by_id(enemy_list, enemy_id):
    """Return the enemy in e_list with e_id"""
    for enemy in enemy_list:
        if enemy.id == enemy_id:
            return enemy
