"""Main file"""


from src.Game import Game

g = Game()


while g.running:
    g.current_menu.display_menu()
    g.game_loop()
