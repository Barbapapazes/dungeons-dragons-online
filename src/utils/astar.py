import math

from pygame.surfarray import array_colorkey
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

    while not to_explore.isEmpty():
        current_tile, current_actions, current_cost = to_explore.pop()
        already_explored[current_tile] = current_cost
        if current_tile != end:
            around_tiles = map.simple_neigh(*current_tile)
            # We want next_tiles to be in the form : (coordonate, path, cost)
            for action, next_tile in around_tiles:
                cost = heuristic(start, end)
                if not (next_tile in already_explored and already_explored[next_tile] < cost):
                    to_explore.push(
                        (next_tile, current_actions + [action], cost), current_cost + cost)
                    already_explored[next_tile] = cost
        else:
            print("---->", current_actions)
            return current_actions
    # If no path is found :
    return []
