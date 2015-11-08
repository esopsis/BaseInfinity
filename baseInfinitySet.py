import pygame
import sys
from random import randrange
from pygame.locals import *
pygame.init()

""" baseInfinitySet.py
by Eric J.Parfitt (ejparfitt@gmail.com)

Base 2 has 2 sybols, base 10 has 10 symbols, so, logically, base
infinity has an infinite number of symbols, one for each non-negative
integer.  This program generates symbols that correspond to such natural
numbers.  This program allows one to either set a starting number in the
code, or, within the program, to set a symbol shape and see what number
it corresponds to.  Some goals for this system were to make relatively
compact symbols, in which all of the parts of the symbol are connected
(so not a QR code for example) and to make it so that it's not too
difficult to tell where in the symbol a sub-part of the symbol is
located in the x,y direction, hence the implementation of a step-like
"base" structure.

Version: 1.0 alpha
"""

WIDTH = 500
HEIGHT = 400

windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

FPS = 60
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
        self.isBase = False
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
    
    def __init__(self, initNum):
        self.number = initNum
        self.LINE_LEN = 20
        self.initPos = (30, 300)
        self.font = pygame.font.Font(None, 30)
        binary, segNum = self.setBinSegnum()
        self.setSegs(binary, segNum)

    def arraySegs(self):
        segments = []
        for i in range(self.width * 2):
            segments.append([])
            if i % 2 == 0:
                for j in range(1, self.width + 1):
                    segments[i].append(Segment((x(self.initPos) +
                            self.LINE_LEN * j, y(self.initPos) -
                            self.LINE_LEN / 2 - self.LINE_LEN * i / 2),
                            self.LINE_LEN / 2, Segment.VERTICAL))
            else:
                for j in range(self.width):
                    segments[i].append(Segment((x(self.initPos) +
                            self.LINE_LEN / 2 + self.LINE_LEN * j,
                            y(self.initPos) - self.LINE_LEN * (i + 1) / 2),
                            self.LINE_LEN / 2, Segment.HORIZONTAL))
        return segments

    def baseSegs(self):
        for i in range(self.width // 2):
            for j in range(self.width * 2 - 2 - 4 * i):
                if j % 2 == 0:
                    segment = self.segments[j + 1 + 4 * i][j / 2]
                    segment.isOn = segment.isBase = True
                else:
                    segment = self.segments[j + 1 + 4 * i][(j - 1) / 2]
                    segment.isOn = segment.isBase = True
        for i in range((self.width - 1) // 2):
            for j in range(2 + 2 * (self.width - 3) - 4 * i):
                if j % 2 == 0:
                    segment = self.segments[j][j / 2 + 1 + 2 * i]
                    segment.isOn = segment.isBase = True
                else:
                    segment = self.segments[j][(j - 1) / 2 + 2 + 2 * i]
                    segment.isOn = segment.isBase = True
        if self.width >= 2:
            segment = self.segments[self.width * 2 - 1][self.width - 1]
            segment.isOn = segment.isBase = True

    def setOpenSegs(self, binary):
        for i in range(len(binary)):
            if int(binary[len(binary) - 1 - i]):
                self.openSegs[i].isOn = True
            else:
                self.openSegs[i].isOn = False

    def getOpenSegs(self, segNum):
        openSegs = []
        for row in self.segments:
            for i in range(len(row)):
                toAdd = row[len(row) - 1 - i]
                if not toAdd.isOn:
                    openSegs.append(toAdd)
        assert segNum == len(openSegs)
        return openSegs

    def setBinSegnum(self):
        self.width = 0
        nextBaseNum = 0
        while(self.number >= nextBaseNum):
            self.width += 1
            segNum = 2 * self.width ** 2
            for i in range(self.width // 2):
                segNum -= 2 * self.width - 2 - 4 * i
            for i in range((self.width - 1) // 2):
                segNum -= 2 * self.width - 4 - 4 * i
            if self.width >= 2:
                segNum -= 1
            self.baseNum = nextBaseNum
            nextBaseNum += 2 ** (segNum)
        binary = "{0:b}".format(self.number - self.baseNum)
        return binary, segNum

    def setSegs(self, binary, segNum):
        self.segments = self.arraySegs()
        self.baseSegs()
        self.openSegs = self.getOpenSegs(segNum)
        self.setOpenSegs(binary)
        

    def update(self, mouseLoc):
        row = (-(y(mouseLoc) - (y(self.initPos) - self.LINE_LEN / 4)) //
                (self.LINE_LEN / 2))
        if row % 2 == 0:
            column = ((x(mouseLoc) - (x(self.initPos) + self.LINE_LEN / 2)) //
                    self.LINE_LEN)
        else:
            column = (x(mouseLoc) - x(self.initPos)) // self.LINE_LEN
        if (0 <= row < len(self.segments) and 0 <= column <
                len(self.segments[row])):
            segment = self.segments[row][column]
            if not segment.isBase:
                i = self.openSegs.index(segment)
                if segment.isOn:
                    segment.isOn = False
                    self.number -= 2 ** i
                else:
                    segment.isOn = True
                    self.number += 2 ** i
        elif column == -1:
            if row == len(self.segments):
                self.incWidth()
            elif row == len(self.segments) - 2:
                self.decWidth()
        elif row == -1:
            if column == self.width:
                self.incWidth()
            elif column == self.width - 1:
                self.decWidth()

    def incWidth(self):
        self.width += 1
        self.baseNum += 2 ** len(self.openSegs)
        segNum = 2 * self.width ** 2
        for i in range(self.width // 2):
            segNum -= 2 * self.width - 2 - 4 * i
        for i in range((self.width - 1) // 2):
            segNum -= 2 * self.width - 4 - 4 * i
        if self.width >= 2:
            segNum -= 1
        self.setSegs("0", segNum)
        self.number = self.baseNum

    def decWidth(self):
        self.width -= 1
        segNum = 2 * self.width ** 2
        for i in range(self.width // 2):
            segNum -= 2 * self.width - 2 - 4 * i
        for i in range((self.width - 1) // 2):
            segNum -= 2 * self.width - 4 - 4 * i
        if self.width >= 2:
            segNum -= 1
        self.setSegs("0", segNum)
        self.baseNum -= 2 ** len(self.openSegs)
        self.number = self.baseNum

    def draw(self):
        windowSurface.fill(WHITE)
        windowSurface.blit(self.font.render(str(self.number), False, BLACK),
                (100 , HEIGHT - 80))
        pygame.draw.line(windowSurface, Segment.COLOR, self.initPos ,
                [x(self.initPos), y(self.initPos) - self.width * self.LINE_LEN])
        pygame.draw.line(windowSurface, Segment.COLOR, self.initPos,
                [x(self.initPos) + self.width * self.LINE_LEN, y(self.initPos)])
        for row in self.segments:
            for self.segment in row:
                self.segment.draw()
        pygame.display.flip()
        clock.tick(FPS)

# Busy beaver number 3 state 3 symbol turing machine steps
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
scene = Scene(0)
scene.draw()
while(True):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            scene.update(pygame.mouse.get_pos())
            scene.draw()
