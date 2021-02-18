import pygame as pg
from Map import Map
from Player import PlayerList
from Foe import FoeList
from Fight import FightList

map = [[0.5 for _ in range(10)] for _ in range(10)]


class Game:
    """Init and take care of evythings and evryone (display, update and detection)"""

    def __init__(self):
        self.map = Map(map)
        self.window = pg.display.set_mode((200, 200))
        self.plist = PlayerList([0, 0, 1, 0], ["m", 0])
        self.flist = FoeList([7, 7, 3, 7], ["m", 0])
        self.clock = pg.time.Clock()
        self.fight = FightList()
        self.mainloop()

    def mainloop(self):
        self.loop = True
        while self.loop:
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(30)

    def update(self):
        if self.plist.cplayer.map[0] == "f":
            cmap = self.fight.flist[self.plist.cplayer.map[1]].fmap.cmap
        else:
            cmap = self.map.cmap
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.loop = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    self.plist.cplayer.x = max(0, self.plist.cplayer.x - 1)
                if event.key == pg.K_UP:
                    self.plist.cplayer.y = max(0, self.plist.cplayer.y - 1)
                if event.key == pg.K_RIGHT:
                    self.plist.cplayer.x = min(
                        self.plist.cplayer.x + 1, len(cmap) - 1
                    )
                if event.key == pg.K_DOWN:
                    self.plist.cplayer.y = min(
                        self.plist.cplayer.y + 1, len(cmap[0]) - 1
                    )
                if event.key == pg.K_TAB:
                    self.plist.nextplayer()
        self.flist.check_player(self.plist, self.fight, self)
        self.fight.new_challenger(self.plist)

    def draw(self):
        self.window.fill((100, 100, 100))
        if self.plist.cplayer.map[0] == "f":
            self.fight.flist[self.plist.cplayer.map[1]].fmap.draw(self.window)
        else:
            self.map.draw(self.window)
            self.fight.draw(self.window)
        self.flist.draw(self.window, self.plist.cplayer.map)
        self.plist.draw(self.window, self.plist.cplayer.map)


Game()