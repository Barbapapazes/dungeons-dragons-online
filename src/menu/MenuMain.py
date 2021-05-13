from src.menu._menu import Menu
from src.interface import Button
from src.config.assets import fonts_folder
from os import path
from src.config.colors import WHITE


class MenuMain(Menu):
    """Defines the main menu with 2 buttons"""

    def __init__(self, game):
        Menu.__init__(self, game)

        self.character_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2,
            "Character Customization",
            path.join(fonts_folder, "enchanted_land.otf"),
            WHITE,
            40,
        )
        self.exit_button = Button(
            self.game,
            self.game.resolution[0] // 2,
            self.game.resolution[1] // 2 + 150,
            "Exit Game",
            path.join(fonts_folder, "enchanted_land.otf"),
            WHITE,
            40,
        )

    def check_events(self, event):
        """This method deals with the user inputs
            on the different buttons of the menu
        Args:
            event (Event) : a pygame event
        """
        if self.character_button.is_clicked(event):
            self.game.current_menu = self.game.character_menu
            self.displaying = False
        if self.exit_button.is_clicked(event):
            self.game.quit()

    def display_menu(self):
        """Displays the menu on our screen"""
        self.displaying = True
        while self.displaying:
            # Checking for events
            self.game.check_events()
            self.game.display.blit(self.menu_background, (0, 0))

            self.character_button.display_button()
            self.character_button.color_on_mouse(WHITE)

            self.exit_button.display_button()
            self.exit_button.color_on_mouse(WHITE)

            self.display_to_game()
            self.game.clock.tick(30)
