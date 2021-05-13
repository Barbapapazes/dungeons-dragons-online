import pygame as pg
import pyperclip
from src.config.colors import INPUT_BOX_BROWN, INPUT_BOX_LIGHT_BROWN, WHITE


class Input(object):
    """This class aims to create text entries where the user can write
    things such as his character name"""

    def __init__(
        self, game, px, py, width, height, font, font_size, max_length, text=""
    ):
        font_size = int(
            font_size
        )  # avoid future bug (when font size is a float)

        self.font_size = font_size

        self.game = game
        self.px = px - width // 2
        self.py = py - height // 2
        self.max_length = max_length
        self.width, self.height = width, height

        # Text color & font
        self.color = INPUT_BOX_BROWN
        self.text = text
        self.font_obj = pg.font.Font(font, font_size)

        # Text surface & the box
        self.text_surface = self.font_obj.render(text, True, self.color)
        self.rect = pg.Rect(self.px, self.py, width, height)
        # True = you can write in the box
        self.active = False

    def handle_events(self, event):
        """This function handles whatever action the player does"""
        # When the box is clicked
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        self.color = INPUT_BOX_LIGHT_BROWN if self.active else INPUT_BOX_BROWN

        # If the user is writing
        if event.type == pg.KEYDOWN:
            if self.active:
                # When pressing Return (<-|)
                if event.key == pg.K_RETURN:
                    self.text = ""
                # When pressing Backspace (<-)
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                # Otherwise, write until the max length is exceeded
                elif event.key == pg.K_v and pg.key.get_mods() & pg.KMOD_CTRL:
                    if len(self.text + pyperclip.paste()) < self.max_length:
                        self.text += pyperclip.paste()
                    else:
                        return
                elif len(self.text) < self.max_length:
                    self.text += event.unicode
                # Don't forget to render after all of this !
                self.text_surface = self.font_obj.render(
                    self.text, True, WHITE
                )

    def display_box(self):
        """This function displays our TextEntry"""
        # Drawing a smooth background (done in an horrible way but will be fixed later)
        s = pg.Surface((self.width, self.height))
        s.set_alpha(100)
        s.fill((198, 183, 146) if self.active else (156, 145, 121))
        self.game.display.blit(s, (self.rect.x, self.rect.y))
        # Adding the text surface to our display
        self.game.display.blit(
            self.text_surface, (self.rect.x + self.font_size / 4,
                                self.rect.y + self.font_size / 4)
        )
        # Drawing the rectangle around our TextEntry
        pg.draw.rect(self.game.display, self.color, self.rect, 2)

    def get_text(self):
        """This function returns the text in our field"""
        return self.text

    def flush_text(self):
        "Resert self.text to empty string"
        # Emptying our text
        self.text = self.text[: -len(self.text)]
        # Rendering the text to be displayed
        self.text_surface = self.font_obj.render(self.text, True, self.color)
