"""Module that contains the Log class"""
import pygame as pg
from src.config.colors import GREY, WHITE


class Log:
    """Log class
    a log is a surface that allows to blit text
    that is automatically blit at the next line if the text is too long"""

    def __init__(
        self, width, height, position, text_color, size, game, combat=True, quest=False
    ):
        self.game = game
        self.width = width
        self.height = height
        self.combat = combat
        self.pos = position
        self.quest = quest
        self.text_color = text_color
        self.title_color = (204, 153, 51)
        self.font_size = size
        self.font = pg.font.SysFont("Cascadia code", size)
        self.log_list = []
        self.background = pg.Surface(
            (self.width, self.height), pg.SRCALPHA, 32)
        self.rect = pg.Rect(*position, width, height)
        self.scroll = 0
        self.line_cpt = 0
        self.update = True

    def add_log(self, new_log, color=WHITE, title=False):
        """# function to add new log in form of a list of tuple
        # example: log.add_log([("Player", "Attack zombie"), ("Zombie", "Attack Player")])"""
        self.text_color = color
        self.update = True
        self.log_list.append([new_log, title])

    def print_log(self, surf):
        """function used to draw the log on the surf gave in args"""
        if self.combat:
            self.update = False
            self.background.fill(GREY)
        else:
            self.background = pg.Surface(
                (self.width, self.height), pg.SRCALPHA, 32)
        self.line_cpt = 0
        i = 1
        while (
            i <= len(self.log_list)
            and self.height > (self.line_cpt - 1 - self.scroll) * self.font_size
        ):
            line = []
            _ = self.log_list[-i][0].split("\n")
            for line_ in _:
                word_to_print = ""
                self.line_cpt += 1
                for word in line_.split():
                    # To print a log in multiple lines if it is too long
                    if self.font.size(word_to_print + word)[0] > self.width:
                        line.append([word_to_print, self.log_list[-i][1]])
                        word_to_print = f"{word} "
                        self.line_cpt += 1
                    else:
                        word_to_print += f"{word} "
                line.append([word_to_print, self.log_list[-i][1]])
            for j, _ in enumerate(line):
                if line[j][1]:
                    text = self.font.render(line[j][0], True, self.title_color)
                else:
                    text = self.font.render(line[j][0], True, self.text_color)
                if self.quest:
                    self.background.blit(
                        text, (5, (j - self.scroll) * self.font_size))
                else:
                    self.background.blit(
                        text,
                        (
                            5,
                            self.height
                            - ((self.line_cpt - self.scroll) - j)
                            * self.font_size,
                        ),
                    )

            i += 1

        surf.blit(self.background, self.pos)

    def event(self, event):
        """function that manages the scroll event"""
        if self.quest:
            if (
                event.type == pg.MOUSEBUTTONDOWN
                and event.button == 4
                and self.rect.collidepoint(event.pos)
            ):
                if self.scroll > 0:
                    self.scroll -= 1
            if (
                event.type == pg.MOUSEBUTTONDOWN
                and event.button == 5
                and self.rect.collidepoint(event.pos)
            ):
                if self.scroll < self.line_cpt - 1:
                    self.scroll += 1
        else:
            if (
                event.type == pg.MOUSEBUTTONDOWN
                and event.button == 5
                and self.rect.collidepoint(event.pos)
            ):
                if self.scroll > 0:
                    self.scroll -= 1
            if (
                event.type == pg.MOUSEBUTTONDOWN
                and event.button == 4
                and self.rect.collidepoint(event.pos)
            ):
                if self.scroll < self.line_cpt - 1:
                    self.scroll += 1
