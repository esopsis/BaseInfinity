import pygame, sys
from pygame.locals import *
pygame.init()

""" baseInfinity.py
by Eric J.Parfitt (ejparfitt@gmail.com)

Base 2 has 2 sybols, base 10 has 10 symbols, so, logically, base
infinity has an infinite number of symbols, one for each non-negative
integer.  This program generates a symbol for each natural number one
at a time.  Some goals for this system were to make relatively compact
symbols, in which all of the parts of the symbol are connected (so not a
QR code for example) and to make it so that it's not too difficult to
tell where in the symbol a sub-part of the symbol is located in the x,y
direction, hence the implementation of a step-like "base" structure.

Version: 1.0 alpha
"""

WIDTH = 500
HEIGHT = 400

windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

FPS = 1
clock = pygame.time.Clock()

def x(position):
    return position[0]
        
def y(position):
    return  position[1]
        
class Segment:
    VERTICAL = 0
    HORIZONTAL = 1
    COLOR = BLACK
    
    def __init__(self, position, radius, orientation):
        self.position = position
        self.radius = radius
        self.orientation = orientation
        self.isOn = False
        
    def draw(self):
        if self.isOn:
            if self.orientation == Segment.HORIZONTAL:
                pygame.draw.line(windowSurface, Segment.COLOR, [x(self.position) -
                        self.radius, y(self.position)], [x(self.position) +
                        self.radius, y(self.position)])
            else:
                pygame.draw.line(windowSurface, Segment.COLOR, [x(self.position),
                        y(self.position) - self.radius], [x(self.position),
                        y(self.position) + self.radius])

class Scene:
    
    def setup(self):
        self.number = 0
        self.LINE_LEN = 30
        self.initPos = (30, 250)
        self.font = pygame.font.Font(None, 30)
        windowSurface.fill(WHITE)
    
    def update(self):
        windowSurface.fill(WHITE)
        windowSurface.blit(self.font.render(str(self.number), False, BLACK),
                (100 , HEIGHT - 50))
        width = 0
        unit = 0
        while(self.number >= unit):
            width += 1
            segNum = 2 * width ** 2
            for i in range(width // 2):
                segNum -= 2 * width - 2 - 4 * i
            for i in range((width - 1) // 2):
                segNum -= 2 * width - 4 - 4 * i
            if width >= 2:
                segNum -= 1
            oldUnit = unit
            unit += 2 ** (segNum)
        binary = "{0:b}".format(self.number - oldUnit)
        pygame.draw.line(windowSurface, Segment.COLOR, self.initPos ,
                [x(self.initPos), y(self.initPos) - width * self.LINE_LEN])
        pygame.draw.line(windowSurface, Segment.COLOR, self.initPos,
                [x(self.initPos) + width * self.LINE_LEN, y(self.initPos)])
        segments = []
        for i in range(width * 2):
            segments.append([])
            if i % 2 == 0:
                for j in range(1, width + 1):
                    segments[i].append(Segment((x(self.initPos) +
                            self.LINE_LEN * j, y(self.initPos) -
                            self.LINE_LEN / 2 - self.LINE_LEN * i / 2),
                            self.LINE_LEN / 2, Segment.VERTICAL))
            else:
                for j in range(width):
                    segments[i].append(Segment((x(self.initPos) +
                            self.LINE_LEN / 2 + self.LINE_LEN * j,
                            y(self.initPos) - self.LINE_LEN * (i + 1) / 2),
                            self.LINE_LEN / 2, Segment.HORIZONTAL))
        for i in range(width // 2):
            for j in range(width * 2 - 2 - 4 * i):
                if j % 2 == 0:
                    segments[j + 1 + 4 * i][j / 2].isOn = True
                else:
                    segments[j + 1 + 4 * i][(j - 1) / 2].isOn = True
        for i in range((width - 1) // 2):
            for j in range(2 + 2 * (width - 3) - 4 * i):
                if j % 2 == 0:
                    segments[j][j / 2 + 1 + 2 * i].isOn = True
                else:
                    segments[j][(j - 1) / 2 + 2 + 2 * i].isOn = True
        if width >= 2:
            segment = segments[width * 2 - 1][width - 1]
            segment.isOn = segment.isBase = True
        openSegs = []
        for row in segments:
            for i in range(len(row)):
                toAdd = row[len(row) - 1 - i]
                if not toAdd.isOn:
                    openSegs.append(toAdd)
        assert segNum == len(openSegs)
        for i in range(len(binary)):
            if int(binary[len(binary) - 1 - i]):
                openSegs[i].isOn = True
            else:
                openSegs[i].isOn = False
        for row in segments:
            for segment in row:
                segment.draw()
        pygame.display.flip()
        self.number += 1
        clock.tick(FPS)

    def checkQuit(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

# Busy beaver 3 state 3 symbol turing machine steps
#scene = Scene(119112334170342540)
# 3^3^3
#scene = Scene(7625597484987)
# rubiks cube combinations
#scene = Scene(43252003274489856000)
# monster group size
#scene = Scene(808017424794512875886459904961710757005754368000000000)
# round(Skewe's number, e^727.951346801)
#scene = Scene(139718208931162614894020948779053029226717691747187305554275818\
#71031308895203532702418624927983561329332764298175701690033706198769226626374\
#69009255977877673535067271993126553666282927727145600118077952565043565227624\
#13978680522145698413588007179416166732191824907765532319192178377948289526366\
#4818447617412282047185)
# floor(pi * googol)
#scene = Scene(314159265358979323846264338327950288419716939937510582097494459\
#23078164062862089986280348253421170679)
#scene = Scene(randrange(0, 10 ** 1200))
scene = Scene()
scene.setup()
while(True):
    scene.update()
    scene.checkQuit()
