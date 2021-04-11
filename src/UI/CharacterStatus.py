import pygame as pg
from src.config.assets import ingame_menus_folder, fonts_folder
from os import path
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
        ) // 2, self.game.resolution[1] // 2 - self.surface.get_width() // 2

        # Builtin text that we will change later
        self.character_name = Text(self.surface, 160, 125, "Personnage", path.join(
            fonts_folder, "alegreya.ttf"), "#2C2A27", 50, True)
        self.future_text = Text(self.surface, 160, 300, "[Les stats du personnage]", path.join(
            fonts_folder, "alegreya.ttf"), "#2C2A27", 14, True)

    def update_data(self):
        """[In the future] Updating stats from character stats"""
        pass

    def create_text(self):
        """Create the texts that go in the surface"""
        pass

    def draw(self):
        """Displays the character status menu"""
        self.flag = False

        # Blurring background
        if self.display:
            self.bis_blurred = self.game.display.copy()
            self.bis_blurred = self.blur_surface(self.bis_blurred)

        while self.display:
            self.update_data()
            self.create_text()

            # Blitting the background
            self.bis = self.bis_blurred.copy()
            self.surface.blit(self.background_sprite, (0, 0))

            # Displaying our texts
            self.character_name.display_text()
            self.future_text.display_text()

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
