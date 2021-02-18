"""Main file"""
import pygame as pg
from src.Game import Game
import signal

pg.init()
pg.mouse.set_cursor(*pg.cursors.tri_left)
g = Game()
signal.signal(signal.SIGINT, signal.SIG_IGN)

while g.running:
    g.current_menu.display_menu()
    g.game_loop()
