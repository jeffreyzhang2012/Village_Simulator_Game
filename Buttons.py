import pygame, os
import Buildings
from Buildings import Building
from Buildings import House
from Buildings import Hut
from Buildings import Barn
from Buildings import Forest
from Resources import Resource
from Villagers import Villager

class Button(pygame.sprite.Sprite):
    image = pygame.image.load('button/1.png')
    length = image.get_width()
    selected = None
    num = len([name for name in os.listdir('button') if ',' not in name])
    clear = None # 'all', 'stone', 'tree'

    def __init__(self,num,d):
        self.sub = False
        self.num = num
        self.id = num
        self.x = d.width - num * Button.length
        self.y = d.height - Button.length
        self.image = pygame.image.load('button/%d.png'%num)
        self.clicked = False
        if self.num > 6: return
        self.info = pygame.image.load('button/info,%d.png'%num)
        self.infoWid,self.infoHei=self.info.get_width(),self.info.get_height()
        self.infoX=self.x+Button.length-self.infoWid
        self.infoY=self.y-self.infoHei
        self.hover = False
        # self.twoClicks = True if num == 5 else False

    def __eq__(self,other):
        return isinstance(other,Button) and self.id == other.id

    def blit_alpha(screen, image, x, y , alpha):
        temp = pygame.Surface((image.get_width(),image.get_height())).convert()
        temp.blit(screen, (-x, -y))
        temp.blit(image, (0, 0))
        temp.set_alpha(alpha)
        screen.blit(temp,(x,y))

    def draw(self,screen,d):
        if self.num<=6 and self.hover:
            screen.blit(self.info,(self.infoX,self.infoY))
        if self.clicked:
            Button.blit_alpha(screen,self.image,self.x,self.y,200)
        else: screen.blit(self.image,(self.x,self.y))

    def click(self,d):
        self.clicked = True
        Button.selector(self,d)

    def house(self,d):
        print(Resource.stone,Resource.wood)
        if not (Resource.stone>=House.reqStone and Resource.wood>=House.reqWood)\
            : d.flag = 'build' ; processFlag(d);return
        d.hoveringBuild = House(d)
        d.hovering = True

    def forest(self,d):
        if not (Resource.stone>=Forest.reqStone and Resource.wood>=Forest.reqWood)\
            : d.flag = 'build' ;processFlag(d);return
        d.hoveringBuild = Forest(d)
        d.hovering = True

    def barn(self,d):
        if not (Resource.stone>=Barn.reqStone and Resource.wood>=Barn.reqWood)\
            : d.flag = 'build' ;processFlag(d);return
        d.hoveringBuild = Barn()
        d.hovering = True

    def hut(self,d):
        if not (Resource.stone>=Hut.reqStone and Resource.wood>=Hut.reqWood)\
            : d.flag = 'build' ;processFlag(d);return
        d.hoveringBuild = Hut()
        d.hovering = True

    def farm(self,d):
        d.farmReady = True
        d.hovering = False
        d.hoveringBuild = None

    def selector(self,d):
        if self.num != 5 and (d.farmReady or d.farmHovering):
            d.farmReady = False; d.farmHovering = False; d.hovFarm = None;
            d.hovering = False
        if isinstance(self,clearButton):
            d.clearReady = True
            d.hovering = False
            if self.num == 1:
                Button.clear = 'all'
            elif self.num == 2:
                Button.clear = 'tree'
            elif self.num == 3:
                Button.clear = 'stone'
        elif self.num == 1:
            Button.house(self,d)
        elif self.num == 2:
            Button.forest(self,d)
        elif self.num == 3:
            Button.barn(self,d)
        elif self.num == 4:
            Button.hut(self,d)
        elif self.num == 5:
            Button.farm(self,d)
        elif self.num == 7:
            speedUp(d)
        elif self.num == 8:
            d.pause = not d.pause
        elif self.num == 9:
            slowDown(d)

def resDeduct(build,d):
    if isinstance(build,House):
        Resource.deducted[0]+=House.reqWood
        Resource.deducted[1]+=House.reqStone
    elif isinstance(build,Forest):
        Resource.deducted[0]+=Forest.reqWood
        Resource.deducted[1]+=Forest.reqStone
    elif isinstance(build,Barn):
        Resource.deducted[0]+=Barn.reqWood
        Resource.deducted[1]+=Barn.reqStone
    elif isinstance(build,Hut):
        Resource.deducted[0]+=Hut.reqWood
        Resource.deducted[1]+=Hut.reqStone

def checkTime(d):
    x,y=pygame.mouse.get_pos()
    for button in d.Buttons:
        if button.num>=7:
            if button.x < x < button.x + Button.length and\
            button.y < y < button.y + Button.length:
                if button.num == 7: speedUp(d)
                elif button.num == 8:
                    d.pause = not d.pause
                elif button.num == 9: slowDown(d)

def speedUp(d):
    if d.speed < 3:
        d.speed += 1
        Villager.vel += 3
        if d.speed == 2: d.tick = 40
        elif d.speed == 1: d.tick = 10
        d.pause = False

def slowDown(d):
    if d.speed>1:
        if d.speed == 2: d.tick = 12
        elif d.speed == 3: d.tick = 20
        d.speed -= 1
        Villager.vel -=3
        d.pause = False

class clearButton(Button):
    num = 3
    def __init__(self,mother,num,d):
        self.sub = True
        self.hover = False
        self.num = num
        self.id = self.num + 60
        self.motherNum = mother.num
        self.x = mother.x - (self.num-1) * Button.length
        self.y = mother.y - Button.length
        self.image = pygame.image.load('button/%d,%d.png'%(mother.num,num))
        self.clicked = False

def checkButtons(x,y,d):
    clickedButton = None
    for button in d.Buttons:
        if button.clicked:
            clickedButton = button
        button.clicked = False;
    clear = False
    for button in d.Buttons:
        if button == clickedButton:
            if button.id == 6: clear = True # clear button clicked
        if button.x < x < button.x + Button.length and\
            button.y < y < button.y + Button.length:
            if button.num != 5: d.farmReady = False
            if button.num >= 7: return True
            if isinstance(button,clearButton):
                if clear: button.click(d) # only when clearing
            else: button.click(d)
            d.clickedButton = Button
            return True

def buttonInit(d):
    d.Buttons = [Button(i+1,d) for i in range(Button.num)]
    d.clearButtons = [clearButton(d.Buttons[5],i+1,d) for i in range(clearButton.num)]
    d.Buttons += d.clearButtons

def drawButtons(screen,d):
    for button in d.Buttons:
        if button in d.clearButtons:
            if d.Buttons[5].clicked:
                for clearButton in d.clearButtons:
                    clearButton.draw(screen,d)
        else: button.draw(screen,d)

def clear(d):
    assert Button.clear != None
    lowR = min(d.clearR,d.clearAnchorR)
    lowC = min(d.clearC,d.clearAnchorC)
    rows = abs(d.clearR-d.clearAnchorR)+1
    cols = abs(d.clearC-d.clearAnchorC)+1
    for drow in range(rows):
        for dcol in range(cols):
            if Button.clear == 'all':
                if (lowR+drow,lowC+dcol) in Resource.placed:
                    Resource.placed[(lowR+drow,lowC+dcol)].marked = True
                    Resource.marked.add((lowR+drow,lowC+dcol))
            else:
                if (lowR+drow,lowC+dcol) in Resource.placed and \
                    Resource.placed[(lowR+drow,lowC+dcol)].name==Button.clear:
                    Resource.placed[(lowR+drow,lowC+dcol)].marked = True
                    Resource.marked.add((lowR+drow,lowC+dcol))

def checkHover(d):
    for button in d.Buttons:
        if isinstance(button,clearButton): continue
        button.hover = False
        x,y = pygame.mouse.get_pos()
        if button.x<=x<=button.x+Button.length and button.y<=y<=d.height:
            button.hover = True

def processFlag(d):
    if isinstance(d.flag,Villager):
        vil = d.flag
        if vil.hunger >= 120:
            d.flagText = '%s the %s has died of hunger.'%(vil.realName,vil.job)
        else:
            d.flagText = '%s has been born' % (vil.realName)
    elif isinstance(d.flag,list):
        vil = d.flag[0]
        d.flagText = '%s has grown up into an adult.'%(vil.realName)
    else: d.flagText = 'Insufficient resources to build building.'
    d.flagWait = 3000
