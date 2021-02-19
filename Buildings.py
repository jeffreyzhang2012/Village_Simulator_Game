import pygame, math

class Wheat(pygame.sprite.Sprite):
    images = [pygame.image.load('resources/wheat %s.png'% i)for i in ['s','m','l']]

    def __init__(self,farm,R,C,d):
        self.size = 1
        self.image = Wheat.images[0]
        self.farm = farm
        self.R,self.C = R,C
        a,b,self.imageWid,self.imageHei = self.image.get_rect()
        self.absX3, self.absY3 = Building.findAbsXYWithRowCol(R,C,d)
        self.absImageX = self.absX3 - self.imageWid/3
        self.absImageY = self.absY3 - self.imageHei/2
        self.prevSize = 1
        self.rows=self.cols=1
        self.BR_Row, self.BR_Col = R,C

    def update(self,d):
        if self.prevSize == int(self.size): return
        self.image = Wheat.images[int(self.size)-1]
        a,b,self.imageWid,self.imageHei = self.image.get_rect()
        R,C = self.R,self.C
        self.absX3, self.absY3 = Building.findAbsXYWithRowCol(R,C,d)
        self.absImageX = self.absX3 - self.imageWid/3
        self.absImageY = self.absY3 - self.imageHei/2
        self.prevSize = int(self.size)

    def draw(self,screen,d):
        X,Y = self.absImageX-d.scrollX, self.absImageY-d.scrollY
        screen.blit(self.image,(X,Y))

    def place(self,BR_Row1,BR_Col1,d):
        # if isinstance(thing,Farm): d.drawAll.insert(0,thing); return
        for i in range(len(d.drawAll)):
            placed = d.drawAll[i]
            if isinstance(placed,Farm): continue
            if abs(placed.BR_Row-BR_Row1)+abs(placed.BR_Col-BR_Col1) >= 15: continue
            BRR2,BRC2=placed.BR_Row,placed.BR_Col;rows,cols=placed.rows,placed.cols
            R1=R2=BRR2-rows+1;R3=R4=BRR2;C1=C4=BRC2-cols+1;C2=C3=BRC2
            if R3 <= BR_Row1 - self.rows: continue
            next = False
            for (R,C) in [(R1,C1),(R2,C2),(R3,C3),(R4,C4)]:
                if R < BR_Row1 and C <= BR_Col1: next = True; break
            if next: continue
            else:
                d.drawAll.insert(i,self); return
                # updateMap(build,BR_Row1,BR_Col1,d); return
        d.drawAll.append(self)

class Building(pygame.sprite.Sprite):
    tally = dict()
    placed = []
    drawAll = []
    radius = pygame.image.load('transparentParalYellow.png')
    decrease = pygame.image.load('tabs/decrease.png')
    increase = pygame.image.load('tabs/increase.png')
    number = pygame.image.load('tabs/number.png')
    decreaseHei=increaseHei=decrease.get_height()
    decreaseWid=increaseWid=decrease.get_width()
    numberWid,numberHei = number.get_width(), number.get_height()
    notBuilt = pygame.image.load('tabs/building.png')
    notBuiltWid,notBuiltHei = notBuilt.get_width(), notBuilt.get_height()
    notBuiltR, notBuiltC = 3,2
    notBuiltdY,notBuiltdX = notBuiltHei/notBuiltR,notBuiltWid/notBuiltC

    def __init__(self):
        self.x = 5
        self.hover = False
        for i in self.images:
            i.convert_alpha()
        self.tabX = self.tabY = 0
        if not isinstance(self,Farm):self.built = False
        self.buildWood = [0,self.reqWood]
        self.completion = 0
        self.buildStone = [0,self.reqStone]
        self.worker = 0
        self.beingMoved=[0,0] # wood, stone

    def checkClicked(row,col,d):
        for build in Building.placed:
            if build.hover:
                d.clickedBuild = build; return True
        return False

    def rotate(self):
        try: a = self.dir # test if the building is directional
        except: pass
        dirs = ['s','e','n','w']
        i = dirs.index(self.dir)
        i += 1; i %= 4
        self.dir = dirs[i]
        self.image = self.images[i]
        self.rows, self.cols = self.cols, self.rows

    def findAbsXYWithRowCol(row,col,d):
        # returns the bottom-right vertice (3rd vertice)
        xShiftEachRow = math.tan(d.angle)*d.gridHei
        Y2 = row*d.gridHei; Y3 = Y2 + d.gridHei
        X1 = col*d.gridWid - Y2*math.tan(d.angle)
        X3 = X1 + d.gridWid - xShiftEachRow
        return X3,Y3

    def blit_alpha(screen, image, x, y , alpha):
        temp = pygame.Surface((image.get_width(),image.get_height())).convert()
        temp.blit(screen, (-x, -y))
        temp.blit(image, (0, 0))
        temp.set_alpha(alpha)
        screen.blit(temp,(x,y))

    def draw(self,screen,d):
        image = self.image
        try:BR_Row, BR_Col = self.BR_Row, self.BR_Col
        except: return
        a,b,imageWid,imageHei = image.get_rect()
        absX3, absY3 = Building.findAbsXYWithRowCol(BR_Row, BR_Col, d)
        X3, Y3 = absX3 - d.scrollX, absY3 - d.scrollY
        self.imageX, self.imageY = X3 - imageWid/2, Y3 - imageHei/2
        if (self.hover or not self.built):
            Building.blit_alpha(screen,self.image,self.imageX,self.imageY,150)
        else: screen.blit(self.image,(self.imageX,self.imageY))

    def drawText(screen,text,size,x,cy,font='arial',color=(0,0,0)):
        font=pygame.font.SysFont(font,size)
        text=font.render(text,True,color)
        y=cy-text.get_height()/2
        screen.blit(text,(x,y))
        # learned from http://www.nerdparadise.com/programming/pygame/part5

    def notBuiltButton(self,x,y,d):
        if not self.buttonY<=y<=self.buttonY+Building.decreaseHei: return
        if self.decreaseX<=x<=self.decreaseX+Building.decreaseWid:
            if not self.worker == 0:
                self.worker -= 1
                d.oldCite = self; d.newCite = None
                d.oldJob = 'builder'
                d.newJob = 'laborer'
                d.manageVil = True
        elif self.increaseX<=x<=self.increaseX+Building.increaseWid:
            if not d.laborers == 0:
                self.worker += 1
                d.oldCite = None; d.newCite = self
                d.oldJob = 'laborer'
                d.newJob = 'builder'
                d.manageVil = True

    def clickButton(self,x,y,d):
        if not self.built: self.notBuiltButton(x,y,d); return
        if not (isinstance(self,Forest) or isinstance(self,Farm) or \
            isinstance(self,Hut)): return
        if not self.buttonY<=y<=self.buttonY+Building.decreaseHei: return
        if self.decreaseX<=x<=self.decreaseX+Building.decreaseWid:
            if not self.worker == 0:
                self.worker -= 1
                d.oldCite = self; d.newCite = None
                if isinstance(self,Forest):d.oldJob = 'forester'
                elif isinstance(self,Farm): d.oldJob = 'farmer'
                elif isinstance(self,Hut): d.oldJob = 'gatherer'
                d.newJob = 'laborer'
                d.manageVil = True
        elif self.increaseX<=x<=self.increaseX+Building.increaseWid:
            if not d.laborers == 0:
                self.worker += 1
                d.oldCite = None; d.newCite = self
                d.oldJob = 'laborer'
                if isinstance(self,Forest):d.newJob = 'forester'
                elif isinstance(self,Farm): d.newJob = 'farmer'
                elif isinstance(self,Hut): d.newJob = 'gatherer'
                d.manageVil = True

    def drawWorkerText(self,screen,d):
        for i in range(2):
            if i >= len(self.workers): break
            cy = self.tabY + (i+2.5)*self.tabDy
            name = self.workers[i]
            Building.drawText(screen,name,20,self.tabX+20,cy)
            if name in House.Malenames:
                screen.blit(House.male,(self.tabX+self.tabDx-30,cy-7))
            elif name in House.Fenames:
                screen.blit(House.female,(self.tabX+self.tabDx-30,cy-7))
        for i in range(2,4):
            if i >= len(self.workers): break
            cy = self.tabY + (i-2+2.5)*self.tabDy
            name = self.workers[i]
            Building.drawText(screen,name,20,self.tabX+20+self.tabWid/2,cy)
            if name in House.Malenames:
                screen.blit(House.male,(self.tabX+self.tabDx*2-30,cy-7))
            elif name in House.Fenames:
                screen.blit(House.female,(self.tabX+self.tabDx*2-30,cy-7))

    def drawNotBuiltButton(self,screen,d):
        self.buttonY = self.tabY + 0.5*Building.notBuiltdY-Building.decreaseHei *0.5
        self.numberX = self.tabX + 1.5*Building.notBuiltdX - Building.numberWid * 0.5
        self.decreaseX = self.numberX - 5 - Building.decreaseWid
        self.increaseX = self.numberX + 5 + Building.decreaseWid
        screen.blit(Building.decrease,(self.decreaseX,self.buttonY))
        screen.blit(Building.number,(self.numberX,self.buttonY))
        screen.blit(Building.increase,(self.increaseX,self.buttonY))

    def drawNotBuiltText(self,screen,d):
        text = '%d/%d'%(self.buildStone[0],self.buildStone[1])
        cy = self.tabY + 1.5*Building.notBuiltdY
        Building.drawText(screen,text,20,self.tabX+40,cy)
        text = '%d/%d'%(self.buildWood[0],self.buildWood[1])
        Building.drawText(screen,text,20,self.tabX+Building.notBuiltdX+40,cy)
        cy = self.tabY + 2.5*Building.notBuiltdY
        text = '%d%% complete'%self.completion
        Building.drawText(screen,text,20,self.tabX+40,cy)
        # draw number of workers
        cx = self.numberX + Building.numberWid*0.5
        cy = self.buttonY + Building.numberHei*0.5
        font=pygame.font.SysFont('arial',20)
        text=font.render(str(self.worker),True,(255,255,255))
        y=cy-text.get_height()/2
        x=cx-text.get_width()/2
        screen.blit(text,(x,y))

    def drawNotBuilt(self,screen,d):
        R,C = self.BR_Row - self.rows - 2, self.BR_Col - self.cols
        absX,absY = Building.findAbsXYWithRowCol(R,C,d)
        absX-=Building.notBuiltWid * 0.7; absY -= Building.notBuiltHei
        xOffset = absX-d.scrollX; yOffset = absY - d.scrollY
        if 0 > xOffset:
            absX -= xOffset
        elif xOffset > d.width-Building.notBuiltWid:
            absX = d.scrollX + d.width - Building.notBuiltWid
        if 0 > yOffset:
            absY -= yOffset
        elif yOffset > d.height-Building.notBuiltHei:
            absY = d.scrollY + d.height - Building.notBuiltHei
        X, Y = absX - d.scrollX, absY-d.scrollY
        screen.blit(Building.notBuilt,(X,Y))
        self.tabX, self.tabY = X, Y
        self.drawNotBuiltButton(screen,d)
        self.drawNotBuiltText(screen,d)
    def __repr__(self):
        return '%s %d' % (self.name,self.num)

    def __eq__(self,other):
        if isinstance(other,Building):
            return self.num==other.num and self.name == other.name

class House(Building):
    image_s = pygame.image.load('buildings/house_s.png')
    image_e = pygame.image.load('buildings/house_e.png')
    image_n = pygame.image.load('buildings/house_n.png')
    image_w = pygame.image.load('buildings/house_w.png')
    tab = pygame.image.load('tabs/house.png')
    Malenames = [['Joe %d' for d in range(30)],\
    'Mark','Tom','Ben','Jack','Ray','Luke','Seb','Roy','Fish','Joe',\
     'Jeff','Lambert','Oleg','Luca','Frank','Ted','Dug','James']
    Fenames = [['Mary %d' for d in range(30)],\
    'Liz','Susan','Ruth','Claire','Amy','Anne','Steph','Kate','Amamda','Kat',\
    'Alice','Judy','Rachel','Erica','Renee','Julia','Diana']
    tabWid, tabHei = tab.get_width(), tab.get_height()
    tabR, tabC = 5, 2
    tabDx = tabWid/tabC; tabDy = tabHei/(1+tabR)
    placed = []
    reqWood = reqStone = 100
    male = pygame.image.load('vil/m.png')
    maleWid,maleHei = male.get_width(), male.get_height()
    female = pygame.image.load('vil/f.png')

    def __init__(self,d,name='House',dir='s'):
        pygame.sprite.Sprite.__init__(self)
        self.image = House.image_s
        self.images = [House.image_s,House.image_e,House.image_n,House.image_w]
        self.name = name
        self.dir = 's'
        self.rows = self.cols = 3
        self.reqWood = 100; self.reqStone = 100
        self.beingTaken = 0 # food
        self.food = 0
        self.workers = []
        self.occupants = dict(); self.adults=0;self.males=0;self.females=0
        super().__init__()

    def moveIn(self,d):
        self.citeSurrounding(d)
        d.moveInVils = True; d.newHouse = self

    def citeSurrounding(self,d):
        R3,C3 = self.BR_Row, self.BR_Col
        rows,cols = self.rows, self.cols
        R4=R3; C2=C3
        R2=R1=R3-(rows-1); C1=C4=C3-(cols-1)
        self.sur = []
        for dcol in range(cols):
            self.sur.append((R1-1,C1+dcol))
            self.sur.append((R4+1,C4+dcol))
        for drow in range(rows):
            self.sur.append((R1+drow,C1-1))
            self.sur.append((R3+drow,C2+1))

    def drawTabText(self,screen,d):
        occu = list(self.occupants.keys())
        for i in range(2):
            if i >= len(occu): break
            cy = self.tabY + (i+2.5)*House.tabDy
            name = occu[i]
            Building.drawText(screen,name,20,self.tabX+20,cy)
            if name in House.Malenames:
                screen.blit(House.male,(self.tabX+House.tabDx-30,cy-7))
            elif name in House.Fenames:
                screen.blit(House.female,(self.tabX+House.tabDx-30,cy-7))
            age = str(int(self.occupants[name]))
            Building.drawText(screen,age,20,self.tabX+House.tabDx-50,cy)
        for i in range(2,4):
            if i >= len(occu): break
            cy = self.tabY + (i-2+2.5)*House.tabDy
            name = occu[i]
            Building.drawText(screen,name,20,self.tabX+20+House.tabWid/2,cy)
            if name in House.Malenames:
                screen.blit(House.male,(self.tabX+House.tabDx*2-30,cy-7))
            elif name in House.Fenames:
                screen.blit(House.female,(self.tabX+House.tabDx*2-30,cy-7))
            age = str(int(self.occupants[name]))
            Building.drawText(screen,age,20,self.tabX+House.tabDx*2-50,cy)
        food = 0 if self.food <=0 else self.food
        Building.drawText(screen,str(food),20,self.tabX+40,\
            self.tabY+5.5*House.tabDy)

    def drawTab(self,screen,d):
        if not self.built: self.drawNotBuilt(screen,d); return
        R,C = self.BR_Row - self.rows - 2, self.BR_Col - self.cols
        absX,absY = Building.findAbsXYWithRowCol(R,C,d)
        absX-=House.tabWid * 0.7; absY -= House.tabHei
        xOffset = absX-d.scrollX; yOffset = absY - d.scrollY
        if 0 > xOffset:
            absX -= xOffset
        elif xOffset > d.width-House.tabWid:
            absX = d.scrollX + d.width - House.tabWid
        if 0 > yOffset:
            absY -= yOffset
        elif yOffset > d.height-House.tabHei:
            absY = d.scrollY + d.height - House.tabHei
        X, Y = absX - d.scrollX, absY-d.scrollY
        screen.blit(self.tab,(X,Y))
        self.tabX, self.tabY = X, Y
        self.drawTabText(screen,d)

class Hut(Building):
    image_s = pygame.image.load('buildings/hunting cabin_s.png')
    image_e = pygame.image.load('buildings/hunting cabin_e.png')
    image_n = pygame.image.load('buildings/hunting cabin_n.png')
    image_w = pygame.image.load('buildings/hunting cabin_w.png')
    reqWood = reqStone = 75
    tab = pygame.image.load('tabs/hut.png')
    tabWid, tabHei = tab.get_width(), tab.get_height()
    tabR, tabC = 3, 2
    placed = []
    tabDx = tabWid/tabC; tabDy = tabHei/(1+tabR)

    def __init__(self,name='Hut',dir='s'):
        pygame.sprite.Sprite.__init__(self)
        self.image = Hut.image_s
        self.images = [Hut.image_s,Hut.image_e,Hut.image_n,Hut.image_w]
        self.name = name
        self.dir = 's'
        self.radius = 15
        self.rows = self.cols = 2
        self.reqWood = self.reqStone = 75
        self.workers = []
        self.coverage = set()
        super().__init__()

    def findCoverage(self,d):
        R,C = self.BR_Row, self.BR_Col
        for i in range(-self.radius,self.radius+1):
            for j in range(-self.radius,self.radius+1):
                if (j**2 + i**2)**0.5 <= self.radius:
                    self.coverage.add((R+i,C+j))

    def drawRadius(self,screen,d):
        if self.coverage == set(): self.findCoverage(d)
        image = Building.radius
        for (R,C) in self.coverage:
            absX3,absY3 = Building.findAbsXYWithRowCol(R,C,d)
            X3,Y3 = absX3 - d.scrollX, absY3 - d.scrollY
            imageX = X3 - d.gridWid
            imageY = Y3 - d.gridHei
            screen.blit(image,(imageX,imageY))

    def drawTabText(self,screen,d):
        cx = self.numberX + Building.numberWid*0.5
        cy = self.buttonY + Building.numberHei*0.5
        font=pygame.font.SysFont('arial',20)
        text=font.render(str(self.worker),True,(255,255,255))
        y=cy-text.get_height()/2
        x=cx-text.get_width()/2
        screen.blit(text,(x,y))

    def drawButton(self,screen,d):
        self.buttonY = self.tabY + 1.5*Hut.tabDy - Building.decreaseHei *0.5
        self.numberX = self.tabX + 1.5*Hut.tabDx - Building.numberWid * 0.5
        self.decreaseX = self.numberX - 5 - Building.decreaseWid
        self.increaseX = self.numberX + 5 + Building.decreaseWid
        screen.blit(Building.decrease,(self.decreaseX,self.buttonY))
        screen.blit(Building.number,(self.numberX,self.buttonY))
        screen.blit(Building.increase,(self.increaseX,self.buttonY))

    def drawTab(self,screen,d):
        if not self.built: self.drawNotBuilt(screen,d); return
        # also with radius
        R,C = self.BR_Row - self.rows - 2, self.BR_Col - self.cols
        absX,absY = Building.findAbsXYWithRowCol(R,C,d)
        absX-=Hut.tabWid * 0.7; absY -= Hut.tabHei
        xOffset = absX-d.scrollX; yOffset = absY - d.scrollY
        if 0 > xOffset:
            absX -= xOffset
        elif xOffset > d.width-Hut.tabWid:
            absX = d.scrollX + d.width - Hut.tabWid
        if 0 > yOffset:
            absY -= yOffset
        elif yOffset > d.height-Hut.tabHei:
            absY = d.scrollY + d.height - Hut.tabHei
        X, Y = absX - d.scrollX, absY-d.scrollY
        self.drawRadius(screen,d)
        screen.blit(self.tab,(X,Y))
        self.tabX, self.tabY = X, Y
        self.drawButton(screen,d)
        self.drawTabText(screen,d)
        self.drawWorkerText(screen,d)

class Barn(Building):
    image_s = pygame.image.load('buildings/barn_s.png')
    image_e = pygame.image.load('buildings/barn_e.png')
    image_n = pygame.image.load('buildings/barn_n.png')
    image_w = pygame.image.load('buildings/barn_w.png')
    tab = pygame.image.load('tabs/barn.png')
    tabWid, tabHei = tab.get_width(), tab.get_height()
    tabR, tabC = 5, 2
    tabDx = tabWid/tabC; tabDy = tabHei/(1+tabR)
    placed = []
    reqWood=200; reqStone = 100

    def __init__(self,name='Barn',dir='s'):
        pygame.sprite.Sprite.__init__(self)
        self.image = Barn.image_s
        self.images = [Barn.image_s,Barn.image_e,Barn.image_n,Barn.image_w]
        self.name = name
        self.dir = 's'
        self.reqWood = 200; self.reqStone = 100
        self.rows = self.cols = 4
        self.wood=self.food=self.stone=0
        self.workers = []
        self.beingTaken=[0,0,0] # wood, stone , food
        super().__init__()
        Barn.placed.append(self)

    def drawTabText(self,screen,d):
        col1text = [self.wood,self.stone,self.food]
        col2text = []
        for i in range(len(col1text)):
            cy = self.tabY + (i+1.5)*self.tabDy
            Building.drawText(screen,str(col1text[i]),20,self.tabX+50,cy)

    def drawTab(self,screen,d):
        if not self.built: self.drawNotBuilt(screen,d); return
        R,C = self.BR_Row - self.rows - 2, self.BR_Col - self.cols
        absX,absY = Building.findAbsXYWithRowCol(R,C,d)
        absX-=House.tabWid * 0.7; absY -= House.tabHei
        xOffset = absX-d.scrollX; yOffset = absY - d.scrollY
        if 0 > xOffset:
            absX -= xOffset
        elif xOffset > d.width-House.tabWid:
            absX = d.scrollX + d.width - House.tabWid
        if 0 > yOffset:
            absY -= yOffset
        elif yOffset > d.height-House.tabHei:
            absY = d.scrollY + d.height - House.tabHei
        X, Y = absX - d.scrollX, absY-d.scrollY
        screen.blit(self.tab,(X,Y))
        self.tabX, self.tabY = X, Y
        self.drawTabText(screen,d)

class Forest(Building):
    image_s = pygame.image.load('buildings/forest.png')
    image_e = pygame.image.load('buildings/forest.png')
    image_n = pygame.image.load('buildings/forest.png')
    image_w = pygame.image.load('buildings/forest.png')
    tab = pygame.image.load('tabs/forester.png')
    tabWid, tabHei = tab.get_width(), tab.get_height()
    tabR, tabC = 3, 2
    placed = []
    tabDx = tabWid/tabC; tabDy = tabHei/(1+tabR)
    reqWood = 125; reqStone = 75

    def __init__(self,d,name='Forester',dir='s'):
        pygame.sprite.Sprite.__init__(self)
        self.reqWood = 125; self.reqStone = 75
        self.coverage = set()
        self.image = Forest.image_s
        self.images = [Forest.image_s,Forest.image_e,\
        Forest.image_n,Forest.image_w]
        self.radius = 15
        self.name = name
        self.dir = 's'
        self.worker = 0
        self.workers = []
        self.rows = self.cols = 3
        super().__init__()
        self.num = len(Forest.placed) + 1
        Forest.placed.append(self)

    def findCoverage(self,d):
        R,C = self.BR_Row, self.BR_Col
        for i in range(-self.radius,self.radius+1):
            for j in range(-self.radius,self.radius+1):
                if (j**2 + i**2)**0.5 <= self.radius:
                    self.coverage.add((R+i,C+j))


    def drawRadius(self,screen,d):
        if self.coverage == set(): self.findCoverage(d)
        image = Building.radius
        for (R,C) in self.coverage:
            absX3,absY3 = Building.findAbsXYWithRowCol(R,C,d)
            X3,Y3 = absX3 - d.scrollX, absY3 - d.scrollY
            imageX = X3 - d.gridWid
            imageY = Y3 - d.gridHei
            screen.blit(image,(imageX,imageY))

    def drawTabText(self,screen,d):
        cx = self.numberX + Building.numberWid*0.5
        cy = self.buttonY + Building.numberHei*0.5
        font=pygame.font.SysFont('arial',20)
        text=font.render(str(self.worker),True,(255,255,255))
        y=cy-text.get_height()/2
        x=cx-text.get_width()/2
        screen.blit(text,(x,y))

    def drawButton(self,screen,d):
        self.buttonY = self.tabY + 1.5*Forest.tabDy - Building.decreaseHei *0.5
        self.numberX = self.tabX + 1.5*Forest.tabDx - Building.numberWid * 0.5
        self.decreaseX = self.numberX - 5 - Building.decreaseWid
        self.increaseX = self.numberX + 5 + Building.decreaseWid
        screen.blit(Building.decrease,(self.decreaseX,self.buttonY))
        screen.blit(Building.number,(self.numberX,self.buttonY))
        screen.blit(Building.increase,(self.increaseX,self.buttonY))

    def drawTab(self,screen,d):
        if not self.built: self.drawNotBuilt(screen,d); return
        # also with radius
        R,C = self.BR_Row - self.rows - 2, self.BR_Col - self.cols
        absX,absY = Building.findAbsXYWithRowCol(R,C,d)
        absX-=Forest.tabWid * 0.7; absY -= Forest.tabHei
        xOffset = absX-d.scrollX; yOffset = absY - d.scrollY
        if 0 > xOffset:
            absX -= xOffset
        elif xOffset > d.width-Forest.tabWid:
            absX = d.scrollX + d.width - Forest.tabWid
        if 0 > yOffset:
            absY -= yOffset
        elif yOffset > d.height-Forest.tabHei:
            absY = d.scrollY + d.height - Forest.tabHei
        X, Y = absX - d.scrollX, absY-d.scrollY
        self.drawRadius(screen,d)
        screen.blit(self.tab,(X,Y))
        self.tabX, self.tabY = X, Y
        self.drawButton(screen,d)
        self.drawTabText(screen,d)
        self.drawWorkerText(screen,d)

class Farm(Building):
    image = pygame.image.load('buildings/farm.png')
    a,b,imageWid,imageHei = image.get_rect()
    tab = pygame.image.load('tabs/farm.png')
    tabWid, tabHei = tab.get_width(), tab.get_height()
    tabR, tabC = 4, 2
    placed = []
    tabDx = tabWid/tabC; tabDy = tabHei/(1+tabR)

    def __init__(self,name='Farm'):
        pygame.sprite.Sprite.__init__(self)
        self.image = Farm.image
        self.name = name
        self.worker = 0
        self.workers = []
        self.built = True
        self.rows = self.cols = 1
        self.wheat = set() # wheat
        self.maturity = 0

    def _init_(self,d):
        self.empty = []
        # self.hover = False
        for drow in range(self.rows):
            for dcol in range(self.cols):
                self.empty.append((self.BR_Row-drow,self.BR_Col-dcol))
    #     self.grow(d)

    def findMaturity(self,d):
        total = 0
        for wheat in self.wheat:
            total += wheat.size
        if len(self.wheat) == 0: self.maturity = 0
        else: self.maturity = (total*100)//(len(self.wheat)*3)

    def blit_alpha(screen, image, x, y , alpha):
        temp = pygame.Surface((image.get_width(),image.get_height())).convert()
        temp.blit(screen, (-x, -y))
        temp.blit(image, (0, 0))
        temp.set_alpha(alpha)
        screen.blit(temp,(x,y))

    def drawButton(self,screen,d):
        self.buttonY = self.tabY + 1.5*Farm.tabDy - Building.decreaseHei *0.5
        self.numberX = self.tabX + 1.5*Farm.tabDx - Building.numberWid * 0.5
        self.decreaseX = self.numberX - 5 - Building.decreaseWid
        self.increaseX = self.numberX + 5 + Building.decreaseWid
        screen.blit(Building.decrease,(self.decreaseX,self.buttonY))
        screen.blit(Building.number,(self.numberX,self.buttonY))
        screen.blit(Building.increase,(self.increaseX,self.buttonY))

    def drawTab(self,screen,d):
        # also with radius
        R,C = self.BR_Row - self.rows - 2, self.BR_Col - self.cols
        absX,absY = Building.findAbsXYWithRowCol(R,C,d)
        absX-=Farm.tabWid * 0.7; absY -= Farm.tabHei
        xOffset = absX-d.scrollX; yOffset = absY - d.scrollY
        if 0 > xOffset:
            absX -= xOffset
        elif xOffset > d.width-Farm.tabWid:
            absX = d.scrollX + d.width - Farm.tabWid
        if 0 > yOffset:
            absY -= yOffset
        elif yOffset > d.height-Farm.tabHei:
            absY = d.scrollY + d.height - Farm.tabHei
        X, Y = absX - d.scrollX, absY-d.scrollY
        screen.blit(self.tab,(X,Y))
        self.tabX, self.tabY = X, Y
        self.drawButton(screen,d)
        self.drawTabText(screen,d)
        self.drawWorkerText(screen,d)

    def drawTabText(self,screen,d):
        cx = self.numberX + Building.numberWid*0.5
        cy = self.buttonY + Building.numberHei*0.5
        font=pygame.font.SysFont('arial',20)
        text=font.render(str(self.worker),True,(255,255,255))
        y=cy-text.get_height()/2
        x=cx-text.get_width()/2
        screen.blit(text,(x,y))
        cy = self.tabY + self.tabDy*4.5
        text = str(self.maturity)
        Building.drawText(screen,text,20,self.tabX+self.tabDx+30,cy)

    def draw(self,screen,d):
        R, C = self.BR_Row, self.BR_Col
        def helper(self,row,col,screen,d):
            absX3, absY3=Building.findAbsXYWithRowCol(row,col,d)
            X3, Y3 = absX3 - d.scrollX, absY3 - d.scrollY
            imageX, imageY = X3 - Farm.imageWid/2,Y3-Farm.imageHei/2
            if (self.hover):
                Building.blit_alpha(screen,self.image,imageX,imageY,150)
            else: screen.blit(self.image,(imageX,imageY))
        for drow in range(abs(self.rows)):
            for dcol in range(abs(self.cols)):
                helper(self,R-drow,C-dcol,screen,d)
        for wheat in self.wheat:
            wheat.draw(screen,d)

    def drawHov(self,screen,d):
        image = self.image
        try:R, C = self.anchorR, self.anchorC
        except: return
        def helper(self,row,col,screen,d):
            absX3, absY3=Building.findAbsXYWithRowCol(row,col,d)
            X3, Y3 = absX3 - d.scrollX, absY3 - d.scrollY
            self.imageX, self.imageY = X3 - Farm.imageWid/2,Y3-Farm.imageHei/2
            if (self.hover):
                Building.blit_alpha(screen,self.image,self.imageX,self.imageY,150)
            else: screen.blit(self.image,(self.imageX,self.imageY))
        for drow in range(abs(self.rows)):
            for dcol in range(abs(self.cols)):
                if self.rows < 0: tempDrow = -1*drow
                else: tempDrow = drow
                if self.cols < 0: tempDcol = -1*dcol
                else: tempDcol = dcol
                helper(self,R-tempDrow,C-tempDcol,screen,d)
