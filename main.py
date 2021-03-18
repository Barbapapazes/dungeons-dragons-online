"""Main file"""
import traceback
import sys
from src.Game import Game

g = Game()

try:
    while g.running:
        g.current_menu.display_menu()
        g.game_loop()
except Exception:
    traceback.print_exc(file=sys.stdout)
    g.quit()
