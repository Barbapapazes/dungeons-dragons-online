"""
src/UI/CharacterStatus.py

This class is the character status sheet where you can find : 
    - Nickname
    - Stats
    - A health bar
    - Money & weight of the inventory

The text is generated from the player statistics 
"""

import pygame as pg
from src.config.assets import ingame_menus_folder, fonts_folder
from os import path
from src.config.colors import DESC_TEXT_COLOR, WHITE
from src.config.fonts import CASCADIA, CASCADIA_BOLD
from src.interface import Text


class CharacterStatus():
    """A character status menu that you can toggle with tab"""

    def __init__(self, game):

        self.game = game

        # Background
        self.background_sprite = pg.transform.scale2x(pg.image.load(
            path.join(ingame_menus_folder, "background.png"))).convert_alpha()

        # Surfaces
        self.surface = pg.Surface(self.background_sprite.get_size())
        self.bis = None
        self.bis_blurred = None

        # Useful flags
        self.display = False
        self.flag = False
        self.clock = pg.time.Clock()

        self.screen_position = self.game.resolution[0] // 2 - self.surface.get_width(
        ) // 2, self.game.resolution[1] // 2 - self.surface.get_height() // 2

        # Texts
        self.static_texts = {}
        self.dynamic_texts = {}

        # Health bar purpose
        self.hp_ratio = self.game.player.health / \
            self.game.player.max_value["health"]

    def create_text(self):
        """Create the texts that go in the surface"""
        self.static_texts["nickname"] = Text(self.surface, 160, 125, str(self.game.player.nickname), path.join(
            fonts_folder, "CascadiaCodeBold.ttf"), DESC_TEXT_COLOR, 30, True)

        # Generating static text
        i = 0
        for key, value in self.game.player.base_stats.items():
            self.static_texts[key] = Text(self.surface, 110, i * 30 + 190, key[0].upper(
            ) + key[1:] + " :", CASCADIA_BOLD, DESC_TEXT_COLOR, 14, False)
            i += 1
        # Same for dynamic texts
        i = 0
        for key, value in self.game.player.stats.items():
            self.dynamic_texts[key] = Text(self.surface, 280, i * 30 + 190, str(
                value), CASCADIA, DESC_TEXT_COLOR, 14, False)
            i += 1

        # Money and weight
        self.dynamic_texts["money"] = Text(self.surface, 75, 30, str(self.game.player.money) + " $", path.join(
            fonts_folder, "CascadiaCodeBold.ttf"), DESC_TEXT_COLOR, 20, False)
        self.dynamic_texts["weight"] = Text(self.surface, 220, 30, str(self.game.player.inventory.get_weight(
        )) + "kg", CASCADIA_BOLD, DESC_TEXT_COLOR, 20, False)

        # Defense and damages
        self.static_texts["defense"] = Text(self.surface, 110, 400, "Defense :", path.join(
            fonts_folder, "CascadiaCodeBold.ttf"), DESC_TEXT_COLOR, 14, False)
        self.dynamic_texts["defense"] = Text(self.surface, 280, 400, str(
            self.game.player.defense), CASCADIA, DESC_TEXT_COLOR, 14, False)
        self.dynamic_texts["damages"] = Text(self.surface, 265, 455, str(self.game.player.damages), path.join(
            fonts_folder, "CascadiaCodeBold.ttf"), DESC_TEXT_COLOR, 22, False)

        # Health amount
        self.dynamic_texts["hp"] = Text(self.surface, 40, 477, str(self.game.player.health) + "/" + str(
            self.game.player.max_value["health"]), CASCADIA, "#ffffff", 14, True)

    def draw(self):
        """Displays the character status menu"""
        self.flag = False

        # Blurring background
        if self.display:
            self.bis_blurred = self.game.display.copy()
            self.bis_blurred = self.blur_surface(self.bis_blurred)
            self.game.player.update_stats()

        while self.display:
            self.create_text()

            # Blitting the background
            self.bis = self.bis_blurred.copy()
            self.surface.blit(self.background_sprite, (0, 0))

            # Health bar
            pg.draw.rect(self.surface, (115, 8, 0), (8, 466, 136, 22))
            pg.draw.rect(self.surface, (22, 148, 20),
                         (8, 466, self.hp_ratio * 126, 22))

            # Displaying our texts
            for key, value in self.static_texts.items():
                value.display_text()
            for key, value in self.dynamic_texts.items():
                value.display_text()

            self.bis.blit(self.surface, self.screen_position)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.display = False
                    self.game.quit()
                if event.type == pg.KEYDOWN:
                    # If we press tab, display the character status menu
                    if event.key == pg.K_TAB:
                        self.display = False

            self.game.window.blit(self.bis, (0, 0))
            self.flag = True
            pg.display.update()
            self.clock.tick(30)

    def blur_surface(self, surface):
        """Blurs the bis_blurred display"""
        for i in range(1, 4):
            surface = pg.transform.smoothscale(
                surface, (self.game.resolution[0] * i, self.game.resolution[1] * i))
            surface = pg.transform.smoothscale(
                surface, (self.game.resolution[0] // i * 2, self.game.resolution[1] // i * 2))
            surface = pg.transform.smoothscale(surface, self.game.resolution)
        return surface
