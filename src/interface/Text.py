import pygame as pg


class Text():
    """A class used to display text on screen, on a specified surface"""

    def __init__(self, surface, px, py, text, font, text_color, font_size, center=True):
        font_size = int(font_size)  # to avoid a bug with float sized fonts

        self.surface = surface
        self.px, self.py = px, py
        self.center = center

        # Text color, size and font
        self.text, self.text_color = text, text_color
        self.font, self.font_size = font, font_size

        # Create the surface
        self.font_obj = pg.font.Font(self.font, self.font_size)
        self.text_surface = self.font_obj.render(
            self.text, True, pg.Color(self.text_color))
        self.rectText = self.text_surface.get_rect()
        if self.center:
            self.rectText.center = (self.px, self.py)
        else:
            # if bugged : try self.recTtext.centery
            self.rectText.x, self.rectText.y = (self.px, self.py)

    def display_text(self):
        """Displays the text"""
        self.surface.blit(self.text_surface, self.rectText)

    def update_text(self, text, center):
        """Updates the current text with a new one"""
        self.text = text
        self.text_surface = self.font_obj.render(
            self.text, True, pg.Color(self.text_color))
        self.rectText = self.text_surface.get_rect()
        if self.center:
            self.rectText.center = (self.px, self.py)
        else:
            # if bugged : try self.recTtext.centery
            self.rectText.x, self.rectText.y = (self.px, self.py)

    def get_width(self):
        return self.rectText.width

    def get_height(self):
        return self.rectText.height

    def get_center(self):
        return self.rectText.center
