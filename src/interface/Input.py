import pygame as pg

BROWN = "#A52A2A"
WHITE = "#FFFFFF"


class Input(object):
    """This class aims to create text entries where the user can write
    things such as his character name"""

    def __init__(
        self, game, px, py, width, height, font, font_size, max_length, text=""
    ):
        font_size = int(
            font_size
        )  # avoid future bug (when font size is a float)

        self.game = game
        self.px = px - width // 2
        self.py = py - height // 2
        self.max_length = max_length
        self.width, self.height = width, height

        # Text color & font
        self.color = BROWN
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
        self.color = WHITE if self.active else BROWN

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
                elif len(self.text) < self.max_length:
                    self.text += event.unicode
                # Don't forget to render after all of this !
                self.text_surface = self.font_obj.render(
                    self.text, True, self.color
                )

    def display_box(self):
        """This function displays our TextEntry"""
        # Adding the text surface to our display
        self.game.display.blit(
            self.text_surface, (self.rect.x + 5, self.rect.y + 5)
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
