import pygame as pg


class Button(object):
    """The button class which is used in our menus"""

    def __init__(
        self, game, px, py, text, font, text_color, font_size, size="large"
    ):

        self.game = game
        self.text = text
        self.font = font
        self.text_color = text_color
        self.font_size = font_size
        self.size = size

        # Background of the Button
        self.button_sprite_path = (
            "src/assets/menus/" + self.size + "_button.png"
        )
        self.hover_sprite_path = (
            "src/assets/menus/" + self.size + "_button_hover.png"
        )
        self.button_background = pg.image.load(
            self.button_sprite_path
        ).convert_alpha()
        self.button_background_hover = pg.image.load(
            self.hover_sprite_path
        ).convert_alpha()

        # Rectangle over the button
        self.x, self.y = (
            px - self.button_background.get_width() // 2,
            py - self.button_background.get_height() // 2,
        )
        self.rect = self.button_background.get_rect(x=self.x, y=self.y)

        # Creating the text display of the button
        self.font_obj = pg.font.Font(font, self.font_size)
        self.text_surface = self.font_obj.render(
            text, True, pg.Color(text_color)
        )
        self.rectText = self.text_surface.get_rect()
        self.rectText.center = self.rect.center

    def color_on_mouse(self, new_color):
        "Changing button color when mouse is passing on it"
        # Testing if the button is pressed
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.game.display.blit(
                self.button_background_hover, (self.x, self.y)
            )  # Changing the button color
            self.hover_text_surface = self.font_obj.render(
                self.text, True, pg.Color(new_color)
            )
            self.game.display.blit(self.hover_text_surface, self.rectText)

    def is_clicked(self, event):
        """Returns true if the button is clicked"""
        return (
            event.type == pg.MOUSEBUTTONDOWN
            and self.rect.collidepoint(pg.mouse.get_pos())
            and event.button == 1
        )

    def display_button(self):
        """Displays the button by bliting it to the game display"""
        self.game.display.blit(self.button_background, (self.x, self.y))
        self.game.display.blit(self.text_surface, self.rectText)
