"""Main file"""
import pygame as pg
from src.Game import Game

pg.init()
pg.mouse.set_cursor(*pg.cursors.tri_left)
g = Game()

while g.running:
    g.current_menu.display_menu()
    g.game_loop()
