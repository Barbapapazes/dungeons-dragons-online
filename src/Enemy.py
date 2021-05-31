from src.config.window import TILE_SIZE
from src.utils.astar import bfs
from random import randint
import pygame as pg


class Enemy:
    def __init__(self, map, e_id):
        self.id = e_id
        self.map = map
        self.image = pg.image.load("src/assets/enemy.png")
        self.tileX, self.tileY = None, None

    def draw(self, display):
        """Draw the ennmy on the display"""
        if self.map.is_visible_tile(self.tileX, self.tileY):
            relativX, relativY = self.map.get_relative_tile_pos(
                self.tileX, self.tileY)
            relativX, relativY = relativX * TILE_SIZE, relativY * TILE_SIZE
            display.blit(self.image, (relativX, relativY))
    
    def get_pos(self):
        return(self.tileX,self.tileY)

    def walk(self, pos):
        self.tileX, self.tileY = pos

class local_Enemy(Enemy):
    def __init__(self, map, e_id):
        super().__init__(map, e_id)
        self.tileX, self.tileY = self.map.get_free_tile()
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

    def act(self, network):
        """Update position, wait or generate a path """
        if randint(0, 15) > 0:
            #We do not act 4 times out of 15
            return
        if len(self.futur_steps) != 0:
            # If we have a path; we continue to go through
            self.walk(self.futur_steps.pop(0))
            network.send_enemy_update(self.id, self.get_pos())
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
        if self.health > 0 :
            return True
            #Send new health to all other player
        #Notify all the player that monster is dead
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

    def take_damage(self, damage):
        """Give damage to enemy"""
        #Send to owner the damage 
        pass
    
def manage_enemy(game):
    "Manage and create the enemy list"
    # Try to create a new enemy
    if game.own_id < 0 :
        #The connection is being established so we wait
        return
    if (len(game.local_enemy_list) < 5) and (randint(0, 20) > 19):
        e_id = len(game.local_enemy_list)
        while (any(e.id == e_id for e in game.local_enemy_list)):
            e_id += 1
        new_e = local_Enemy(game.world_map, e_id)
        game.network.send_enemy_update(new_e.id, new_e.get_pos(), isNewEnemy=True)
        game.local_enemy_list.append(new_e)
        
    for e in game.local_enemy_list:
        e.act(game.network)
        e.draw(game.display)

def find_enemy_by_id(enemy_list, enemy_id):
    """Return the enemy in e_list with e_id"""
    print("Finding ", enemy_id, "list is", enemy_list)
    for enemy in enemy_list :
        print("Checking ", enemy.id)
        if enemy.id == enemy_id :
            return enemy