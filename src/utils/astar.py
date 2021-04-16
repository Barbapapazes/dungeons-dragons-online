import math
import pygame as pg
from src.utils.priorityqueue import PriorityQueue


def birdsEyeDistance(start, end):
    """Return bird's eye distance between start and end"""
    return math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)


def aStarSearch(start, end, map, heuristic=birdsEyeDistance):
    """Return list of to go through between start and end
    U : Up ; L : Left ; D : Down ; R : Right ; UL : Up left, etc.."""
    to_explore = PriorityQueue()
    already_explored = dict()
    to_explore.push((start, [], 0), 0)
    compt = 0
    while not to_explore.isEmpty():
        compt += 1
        current_tile, current_actions, current_cost = to_explore.pop()
        already_explored[current_tile] = current_cost
        if current_tile != end and compt < 10:
            around_tiles = map.simple_neigh(*current_tile)
            # We want next_tiles to be in the form : (coordonate, path, cost)
            for action, next_tile in around_tiles:
                cost = heuristic(start, end)
                if not (next_tile in already_explored.keys() and already_explored[next_tile] < cost):
                    to_explore.push(
                        (next_tile, current_actions + [action], cost), current_cost + cost)
                    already_explored[next_tile] = cost
        else:
            return current_actions
    # If no path is found :
    return []


def bfs(start, end, map):
    """Search a path without heuristic"""
    to_explore = []
    already_explored = []
    to_explore.append((start, []))

    while len(to_explore) != 0:
        current_node, action = to_explore.pop(0)  # FIFO
        if current_node not in already_explored:
            already_explored.append(current_node)
            if current_node != end:
                next_nodes = map.neighbor_list(*current_node)
                for next_node, next_action in next_nodes:  # on les ajoute tous a la liste
                    to_explore.append(
                        (next_node, action + [next_action]))
            else:
                return action
    return []
