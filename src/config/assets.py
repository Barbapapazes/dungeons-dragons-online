"""assets config"""
from os import path

game_folder = path.dirname(".")
src_folder = path.join(game_folder, "src")
assets_folder = path.join(src_folder, "assets")

fonts_folder = path.join(assets_folder, "fonts")
menus_folder = path.join(assets_folder, "menus")
ingame_menus_folder = path.join(assets_folder, "ingame-menus")
item_data_folder = path.join(src_folder, "items_data")
