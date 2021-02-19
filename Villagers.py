import pygame, math, random
from Maze import Maze
from Resources import Resource
import Resources
from Resources import Stone
from Buildings import Farm
from Resources import Tree
from Buildings import Building
from Buildings import Hut
from Buildings import Forest
from Buildings import Barn
from Buildings import House
from Buildings import Wheat

def reassignJobs(cite,d):
    for vil in Villager.pop:
        if vil.cite == cite:
            Builder.pop.pop(Builder.pop.index(vil))
            renumber(Builder.pop)
            vil.__class__ = Laborer
            vil._init_(d)
            renumber(Laborer.pop)
            vil.cite = None
            vil.wait=vil.waited=0
            d.laborers += 1
            vil.moving = True

def ImageInit():
    left=[]; right = []; up = []; down = []
    types = ['m','f','mbaby','fbaby']
    for i in range(len(types)):
        s = types[i]
        left.append([pygame.image.load('vil/%s/L%d.png'%(s,j))for j in range(1,12)])
        right.append([pygame.image.load('vil/%s/R%d.png'%(s,j))for j in range(1,12)])
        up.append([pygame.image.load('vil/%s/U%d.png'%(s,j))for j in range(1,7)]*2)
        down.append([pygame.image.load('vil/%s/D%d.png'%(s,j))for j in range(1,7)]*2)
    return (left, right, up, down)

class Villager(pygame.sprite.Sprite):
    pop = []
    vel = 7
    angle = (90-25)*math.pi/180
    xVel = math.cos(angle)*vel; yVel = math.sin(angle)*vel
    (left,right,up,down)=ImageInit()
    # left = [[pygame.image.load('vil/m/L%d.png'%i) for i in range(1,12)]]
    # right = [[pygame.image.load('vil/R%d.png'%i) for i in range(1,12)]]
    # up = [[pygame.image.load('vil/U%d.png'%i) for i in range(1,7)]*2]
    # down = [[pygame.image.load('vil/D%d.png'%i) for i in range(1,7)]*2]
    wid,hei = left[0][0].get_size()
    Malenames = [['Joe %d' for d in range(30)],\
    'Mark','Tom','Ben','Jack','Ray','Luke','Seb','Roy','Fish','Joe',\
     'Jeff','Lambert','Oleg','Luca','Frank','Ted','Dug','James']
    Fenames = [['Mary %d' for d in range(30)],\
    'Liz','Susan','Ruth','Claire','Amy','Anne','Steph','Kate','Amamda','Kat',\
    'Alice','Judy','Rachel','Erica','Renee','Julia','Diana']
    tab = pygame.image.load('tabs/vil.png')
    tabWid, tabHei = tab.get_width(), tab.get_height()
    tabR, tabC = 5, 2
    tabDx = tabWid/tabC; tabDy = tabHei/(1+tabR)
    adulthood = 5
    hungryCap = 100
    males=females=babies=idle=0

    def __init__(self,gender,d):
        self.gender = gender; self.num = len(Villager.pop) + 1
        self.home = None
        self.realName = Villager.Malenames.pop() if gender=='m' else\
             Villager.Fenames.pop()
        self.cite = None
        self.age += random.randint(0,9)*0.1
        self.hunger = 50
        self.reqRes = [0,0]
        self.food = 0
        self.row = 60; self.col = 70; self.cols = 1; self.rows = 1
        self.BR_Row, self.BR_Col = self.row, self.col
        self.absX,self.absY = Villager.centerAbsXY(self.row,self.col,d)
        self.frame = 1
        self.queue = [] # 2d list
        self.dir = ''
        self.nextX,self.nextY =(Villager.centerAbsXY(self.row,self.col,d))
        self.walkImages = Villager.down
        self.moving = True; self.collecting = True
        self.stone = self.wood = 0
        self.idle = True
        self.arrived = False
        self.updateDraw(d)
        self.wait = 0
        self.waited = 0
        if isinstance(self,Baby): Villager.babies += 1
        elif self.gender=='m': Villager.males += 1
        elif self.gender=='f': Villager.females += 1
        # self.clicked = False
        Villager.pop.append(self)

    def __repr__(self):
        return self.name

    def centerAbsXY(row,col,d):
        # returns the bottom-right vertice (3rd vertice)
        xShiftEachRow = math.tan(d.angle)*d.gridHei
        Y2 = row*d.gridHei; Y3 = Y2 + d.gridHei
        X1 = col*d.gridWid - Y2*math.tan(d.angle)
        X3 = X1 + d.gridWid - xShiftEachRow
        return (X1+X3)/2,(Y2+Y3)/2 # middle of the cell

    def drawTabText(self,screen,d):
        # first line
        cy = self.tabY + 0.5*Villager.tabDy
        text1 = '%s  %s         Age: %d'%(self.realName,self.job, self.age)
        Building.drawText(screen,text1,20,self.tabX+20,cy)
        image = House.male if self.gender=='m' else House.female
        screen.blit(image,(self.tabX+Villager.tabWid-35,cy-7))
        #state
        cy = self.tabY + 5.5*Villager.tabDy
        if self.state == 'collecting':
            text = 'collecting natural resources'
        elif self.state == 'idle':
            text = 'walking around'
        elif self.state == 'barn':
            text = 'returning resources to barn'
        elif self.state == 'plant':
            text = 'planting crops' if isinstance(self,Farmer) else 'planting trees'
        elif self.state == 'harvest':
            text = 'harvesting crops'
        elif self.state == 'prune':
            text = 'pruning crops'
        elif self.state == 'transport':
            text = 'moving resources to building cite'
        elif self.state == 'build':
            text = 'working on a construction project'
        elif self.state == 'get food':
            text = 'bringing food back to home'
        elif self.state == 'go home':
            text = 'going home to eat'
        elif self.state == 'gather':
            text = 'gathering wild fruits and vegetables'
        Building.drawText(screen,text,20,self.tabX+20,cy)
        self.drawRes(screen,d)

    def drawRes(self,screen,d):
        texts = [self.wood,self.stone,self.food]
        for i in range(len(texts)):
            text = str(texts[i])
            cy = self.tabY + (i+1.5)*Villager.tabDy
            Building.drawText(screen,text,20,self.tabX+40,cy)
        text = 'hunger: %d%%'%self.hunger
        Building.drawText(screen,text,20,self.tabX+20,self.tabY+4.5*Villager.tabDy)

    def drawTab(self,screen,d):
        R,C = self.BR_Row - self.rows - 2, self.BR_Col - self.cols
        absX,absY = Building.findAbsXYWithRowCol(R,C,d)
        absX-=Villager.tabWid * 0.7; absY -= Villager.tabHei
        xOffset = absX-d.scrollX; yOffset = absY - d.scrollY
        if 0 > xOffset:
            absX -= xOffset
        elif xOffset > d.width-Villager.tabWid:
            absX = d.scrollX + d.width - Villager.tabWid
        if 0 > yOffset:
            absY -= yOffset
        elif yOffset > d.height-Villager.tabHei:
            absY = d.scrollY + d.height - Villager.tabHei
        X, Y = absX - d.scrollX, absY-d.scrollY
        screen.blit(self.tab,(X,Y))
        self.tabX, self.tabY = X, Y
        self.drawTabText(screen,d)

    def nextCheckpoint(self,d):
        # print(self.queue)
        Villager.updateDraw(self,d)
        if self.queue == []: self.moving=False; self.arrived=self.idle=True;return
        # print(self.nextRow,self.nextCol,'next')
        if (self.row, self.col) == (self.nextRow, self.nextCol):
            self.queue.pop(0)
            self.frame = 1
            if self.queue == []: self.moving=False; self.arrived=self.idle=True; return
            [self.nextRow, self.nextCol] = self.queue[0]
            self.nextX,self.nextY = Villager.centerAbsXY(self.nextRow,self.nextCol,d)
            if self.nextRow>self.row: self.dir = 'D';self.walkImages=Villager.down
            elif self.nextRow<self.row: self.dir = 'U';self.walkImages=Villager.up
            elif self.nextCol<self.col: self.dir = 'L';self.walkImages=Villager.left
            elif self.nextCol>self.col: self.dir = 'R';self.walkImages=Villager.right

    def update(self,d): # runs every frame
        if self.dir == 'L':
            self.absX -= self.vel
            if self.absX <= self.nextX:
                self.col = self.nextCol; Villager.nextCheckpoint(self,d)
        elif self.dir == 'R':
            self.absX += self.vel
            if self.absX >= self.nextX:
                self.col = self.nextCol; Villager.nextCheckpoint(self,d)
        elif self.dir == 'U':
            self.absX += self.xVel; self.absY -= self.yVel
            if self.absY <= self.nextY:
                self.row = self.nextRow; Villager.nextCheckpoint(self,d)
        elif self.dir == 'D':
            self.absX -= self.xVel; self.absY += self.yVel
            if self.absY >= self.nextY:
                self.row = self.nextRow; Villager.nextCheckpoint(self,d)

    def solveMaze(self, trgR, trgC, Maze, d):
        [row, col] = self.queue[-1] if self.queue!=[] else [self.row, self.col]
        if trgR==None or trgC == None: return
        if d.gameMap[trgR][trgC]=='farm' and isinstance(self,Farmer):pass
        elif d.gameMap[trgR][trgC] != 'land' and not (isinstance(self,Laborer)\
            or isinstance(self,Forester)): return
        self.trgR,self.trgC = trgR,trgC
        topR = row if row <= trgR else trgR
        topC = col if col <= trgC else trgC
        rows = abs(trgR-row)+1; cols = abs(trgC-col)+1
        def solve():
            maze = [[None]*cols for row in range(rows)]
            for drow in range(rows):
                for dcol in range(cols):
                    cell = d.gameMap[topR+drow][topC+dcol]
                    if cell == 'land' or (isinstance(self,Farmer) and cell=='farm'):
                        maze[drow][dcol] = True
                    else: maze[drow][dcol] = None
            if self.collecting:
                maze[trgR-topR][trgC-topC] = True
                maze[row-topR][col-topC] = True
            return Maze.solveMaze(maze,topR,topC,row,col,trgR,trgC)
        soln = solve(); i = 1
        while soln == None:
            topR-=1; topC-=1; rows += 2; cols += 2
            i += 1
            if i >= 20: return
            soln = solve()
        self.queue += soln
        if len(self.queue) == len(soln) != 0:
            self.nextRow,self.nextCol = self.queue[0][0],self.queue[0][1]
            self.moving = True; Villager.initDir(self,d)

    def initDir(self,d):
        self.frame = 1
        self.nextX,self.nextY = Villager.centerAbsXY(self.nextRow,self.nextCol,d)
        if self.nextRow>self.row: self.dir = 'D';self.walkImages=Villager.down
        elif self.nextRow<self.row: self.dir = 'U';self.walkImages=Villager.up
        elif self.nextCol<self.col: self.dir = 'L';self.walkImages=Villager.left
        elif self.nextCol>self.col: self.dir = 'R';self.walkImages=Villager.right

    def draw(self,screen,d):
        if self.idle: self.action(d)
        imageX = self.absX - d.scrollX - 0.5*Villager.wid
        imageY = self.absY - d.scrollY - Villager.hei
        if isinstance(self,Baby):
            num = 2 if self.gender=='m' else 3
        else: num = 0 if self.gender=='m' else 1
        screen.blit(self.walkImages[num][self.frame],(imageX,imageY))
        if not self.moving: return
        self.frame += 1
        self.frame %= len(self.walkImages[0])

    def findWayOut(self,d):
        drow= dcol = 1
        while True:
            for i in range(-drow,drow+1):
                for j in range(-dcol,dcol+1):
                    tile = d.gameMap[self.row+i][self.col+j]
                    if tile == 'land':
                        self.row,self.col = self.row+i,self.col+j
                        self.absX,self.absY=Villager.centerAbsXY(self.row,self.col,d)
                        if self.state=='idle':
                            self.arrived = True
                            self.queue = []; self.idle = True
                            return
                        if self.queue!=[]:
                            self.queue = self.queue[self.queue.index([self.trgR,self.trgC])+1:]
                        self.solveMaze(self.trgR,self.trgC,Maze,d)
                        if not self.moving: return
                        try:
                            [self.nextRow, self.nextCol] = self.queue[0]
                            self.nextX,self.nextY = Villager.centerAbsXY(self.nextRow,self.nextCol,d)
                        except: pass
                        self.update(d)
                        return
                    else:
                        drow += 1; dcol += 1

    def placeVil(self,BR_Row1, BR_Col1, d):
        if self in d.drawAll:
            d.drawAll.pop(d.drawAll.index(self))
        for i in range(len(d.drawAll)):
            placed = d.drawAll[i]
            if isinstance(placed,Farm): continue
            BRR2,BRC2=placed.BR_Row,placed.BR_Col
            if abs(placed.BR_Row-BR_Row1)+abs(placed.BR_Col-BR_Col1) >= 8: continue
            rows,cols=placed.rows,placed.cols
            R1=R2=BRR2-rows+1;R3=R4=BRR2;C1=C4=BRC2-cols+1;C2=C3=BRC2
            if R3 <= BR_Row1 - self.rows: continue
            next = False
            for (R,C) in [(R1,C1),(R2,C2),(R3,C3),(R4,C4)]:
                if R < BR_Row1 and C <= BR_Col1: next = True; break
            if next: continue
            else:
                d.drawAll.insert(i,self); return
        d.drawAll.append(self)

    def wait(self,time):
        self.wait = time
        self.waited = 0

    def updateDraw(self,d):
        self.BR_Row,self.BR_Col = self.row,self.col
        if d.gameMap[self.row][self.col] != 'land':
            try:self.move(self.trgR,self.trgC,Maze,d); return
            except: pass
        Villager.placeVil(self,self.BR_Row,self.BR_Col,d)

    def eat(self,Food):
        pass

    def move(self,trgR,trgC,Maze,d):
        self.moving = True
        self.trgR, self.trgC = trgR, trgC
        # self.targets.append((self.trgR,self.trgC))
        if d.gameMap[self.row][self.col]=='farm' and isinstance(self,Farmer):
            self.solveMaze(trgR,trgC,Maze,d)
        elif d.gameMap[self.row][self.col] != 'land'and not \
            (((isinstance(self,Laborer) and self.state!='idle') \
                or isinstance(self,Forester))and \
                self.idle == False):
            Villager.findWayOut(self,d)
        else: self.solveMaze(trgR,trgC,Maze,d)

    def walkAround(self,d):
        dis = 3
        while True:
            dR = random.randint(-dis,dis)
            dC = random.randint(-dis,dis)
            if dR == 0 and dC == 0: continue
            if d.gameMap[self.row+dR][self.col+dC] == 'land':
                self.idle = False; self.arrived = False
                self.move(self.row+dR,self.col+dC,Maze,d)
                Villager.wait(self,300)
                return
            dis += 1

    def goToBarn(self,d):
        self.arrived = self.idle = False
        shortest = 1000; trgR=trgC=None
        item = None
        if Building.placed == []: self.idle = True; return
        for build in Building.placed:
            if isinstance(build,Barn):
                (row,col) = build.BR_Row, build.BR_Col
                dis = abs(row-self.row)+abs(col-self.col)
                if dis<shortest:
                    shortest = dis
                    self.barn = build
                    for dcol in range(build.cols):
                        if d.gameMap[row+1][col-dcol] == 'land':
                            (trgR,trgC) = (row+1,col-dcol)
        if shortest == 1000: self.idle = True; return
        self.move(trgR,trgC,Maze,d)

    def kickOut(self):
        del self.home.occupants[self.realName]
        if self.age >= Villager.adulthood:
            self.home.adults -= 1
            if self.gender == 'm': self.home.males -= 1
            else: self.home.females-=1
        self.home = None

    def newHouse(self,house):
        self.home = house
        house.occupants[self.realName] = self.age
        if self.age >= Villager.adulthood:
            house.adults += 1
            if self.gender == 'm': house.males += 1
            elif self.gender == 'f': house.females += 1

    def getFood(self,d):
        shortest = 1000; trgR=trgC=None
        item = None
        for barn in Barn.placed:
            remainFood = barn.food - barn.beingTaken[2]
            if remainFood > 0:
                self.takeFood = remainFood if remainFood<=50 else 50
                self.barn = barn
                (row,col) = barn.BR_Row, barn.BR_Col
                dis = abs(row-self.row)+abs(col-self.col)
                if dis<shortest:
                    shortest = dis
                for dcol in range(barn.cols):
                    if d.gameMap[row+1][col-dcol] == 'land':
                        (trgR,trgC) = (row+1,col-dcol)
        if shortest == 1000: self.idle = True; return
        self.state = 'get food'; self.idle = False; self.arrived = False
        self.barn.beingTaken[2] += self.takeFood
        self.move(trgR,trgC,Maze,d)

    def takeAwayFood(self,d):
        self.barn.beingTaken[2] -= self.takeFood
        self.food += self.takeFood
        self.barn.food -= self.takeFood
        self.takeFood = 0

    def goHome(self,d):
        if self.hunger >= self.home.food - self.home.beingTaken:
            self.home.beingTaken = self.home.food
            # self.eatFood = self.home.food - self.home.beingTaken
        elif self.hunger <= self.home.food - self.home.beingTaken:
            self.home.beingTaken += self.hunger
            # self.eatFood = self.hunger
        self.arrived = self.idle = False
        self.state = 'go home'
        for (R,C) in self.home.sur:
            if d.gameMap[R][C] == 'land':
                self.move(R,C,Maze,d)
                return

    def dropFood(self,d):
        self.home.food += self.food
        self.food = 0
        self.state = 'idle'

    def eat(self,d):
        if self.hunger > self.home.food - self.home.beingTaken:
            self.hunger -= self.home.food - self.home.beingTaken
            self.ate = self.home.food - self.home.beingTaken
            self.home.food = self.home.beingTaken
        else:
            self.home.food -= self.hunger
            self.ate = self.hunger
            self.hunger = 0
        self.home.beingTaken -= self.ate
        self.state = 'idle'

    def foodAction(self,d):
        if self.state == 'idle':
            if self.hunger >= 0.5*Villager.hungryCap and self.home.food-\
             self.home.beingTaken >= 20:
                self.goHome(d); return True
            elif self.home.food - self.home.beingTaken <= 50 and Resource.food >= 20:
                self.getFood(d); return True
        elif self.state == 'get food' and self.arrived:
            self.takeAwayFood(d)
            self.goHome(d)
            return True
        elif self.state == 'go home' and self.arrived:
            self.dropFood(d); self.eat(d); return True

class Baby(Villager):
    pop = []
    def __init__(self,gender,d,age):
        Baby.pop.append(self)
        self.name = 'baby ' + str(len(Baby.pop))
        self.state = 'idle'; self.job = 'baby'
        self.age = age; self.idle = True
        super().__init__(gender,d)

    def action(self,d):
        if self.home != None:
            if self.foodAction(d): return

class Laborer(Villager):
    pop = []
    beingCollected = set()

    def __init__(self,gender,d,age):
        Laborer.pop.append(self)
        self.barn = Barn.placed[0]
        self.name = 'laborer ' + str(len(Laborer.pop))
        self.state = 'idle'; self.job = 'laborer'
        self.age = age
        self.removeR = self.removeC = 0
        super().__init__(gender,d)

    def _init_(self,d):
        if len(Laborer.pop) == 0: Laborer.beingCollected = set()
        Laborer.pop.append(self)
        self.name = 'laborer ' + str(len(Laborer.pop))
        self.state = 'idle'; self.moving = True
        self.idle = True; self.job = 'laborer'
        self.queue = []
        self.nextX,self.nextY =(Villager.centerAbsXY(self.row,self.col,d))
        self.arrived = False
        self.removeR = self.removeC = 0

    def action(self,d):
        if self.home != None:
            if self.foodAction(d): return
        if self.state == 'idle':
            if len(Laborer.beingCollected)!=len(Resource.marked):
                self.goToRes(d)
        elif self.arrived and self.state == 'collecting':
            if not self.wait: Villager.wait(self,10000); return
            elif self.waited < 5000: return
            self.wait=self.waited = 0
            self.removeRes(d)
            if self.stone + self.wood >= 30:
                self.goToBarn(d)
                self.state = 'barn'
            elif self.stone != 0 or self.wood != 0:
                if len(Laborer.beingCollected)==len(Resource.marked):
                    self.goToBarn(d)
                    self.state = 'barn'
                else:
                    self.goToRes(d) # still collecting more
        elif self.state == 'barn' and self.arrived:
            self.barn.stone += self.stone; self.barn.wood += self.wood
            self.stone = self.wood = 0
            self.idle = True; self.state = 'idle'
        # self.carryStone,self.carryStone = self.stone, self.wood
        # self.stone = self.wood = 0

    def removeRes(self,d):
        res = Resource.placed[(self.row,self.col)]
        if res.name=='stone':
            self.stone += 12
        elif res.name=='tree':
            self.wood += 5*2**(res.size-1)
        del Resource.placed[(self.row,self.col)]
        d.gameMap[self.row][self.col] == 'land'
        if res.name == 'stone':
            Stone.placed.pop(Stone.placed.index(res))
        else: d.drawAll.pop(d.drawAll.index(res))
        Resource.marked.remove((self.row,self.col))
        Laborer.beingCollected.remove((self.row,self.col))

    def goToRes(self,d):
        # print(Resource.marked)
        shortest = 1000; trgR=trgC=None
        item = None
        for i in Resource.marked:
            (row,col) = i
            if i in Laborer.beingCollected:
                continue
            dis = abs(row-self.row)+abs(col-self.col)
            if dis<shortest:
                shortest = dis
                trgR,trgC = row,col
        if shortest == 1000: self.idle = True; return
        (self.removeR, self.removeC) = (trgR,trgC)
        Laborer.beingCollected.add((trgR,trgC))
        self.move(trgR,trgC,Maze,d)
        self.arrived = self.idle = False
        self.state = 'collecting'

class Forester(Villager):
    pop = []
    beingCollected = []
    beingPlanted = set()

    def __init__(self,gender,d):
        Forester.pop.append(self)
        self.name = 'forester ' + str(len(Forester.pop))
        self.state = 'idle'; self.idle = True
        self.queue = []; self.job = 'Forester'
        super().__init__(gender,d,home)

    def _init_(self,d):
        if len(Forester.pop) == 0:
            Forester.beingCollected=[]
            Forester.beingPlanted=set()
        Forester.pop.append(self); self.job = 'Forester'
        self.name = 'forester ' + str(len(Forester.pop))
        self.state = 'idle'; self.idle = True
        self.queue = []; self.dir = ''
        self.nextX,self.nextY =(Villager.centerAbsXY(self.row,self.col,d))
        self.arrived = True; self.moving = True
        self.updateDraw(d)

    def action(self,d):
        if self.home != None:
            if self.foodAction(d): return
        if self.state == 'idle':
            if self.checkChop(d):
                self.moveToRes(d)
            cites = self.plantCite(d)
            if len(cites) > 0:
                (R,C) = cites[0]
                if (R,C) in Forester.beingPlanted:
                    return
                self.move(R,C,Maze,d)
                Forester.beingPlanted.add((R,C))
                self.state = 'plant'
                self.arrived = self.idle = False
        elif self.state == 'plant' and self.arrived:
            self.plant(d)
        elif self.state == 'collecting' and self.arrived:
            if not self.wait: Villager.wait(self,10000); return
            elif self.waited < 5000: return
            self.wait=self.waited = 0
            self.chop(d)
            if self.wood >= 40:
                self.goToBarn(d)
                self.state = 'barn'
            elif self.wood != 0:
                if self.checkChop(d):
                    self.moveToRes(d)
                else:
                    self.state = 'idle'; self.idle = True
        elif self.state == 'barn' and self.arrived:
            self.barn.stone += self.stone; self.barn.wood += self.wood
            self.stone = self.wood = 0
            self.idle = True; self.state = 'idle'

    def checkChop(self,d):
        for (R,C) in self.cite.coverage:
            if not (R,C) in Resource.placed: continue
            item = Resource.placed[(R,C)]
            if isinstance(item,Tree) and item.size == 3:
                if item in Forester.beingCollected: continue
                Forester.beingCollected.append((item))
                return True
        return False

    def moveToRes(self,d):
        self.state = 'collecting'; self.idle = False; self.arrived = False
        tree = Forester.beingCollected[-1]
        self.move(tree.BR_Row,tree.BR_Col,Maze,d)

    def chop(self,d):
        res = Resource.placed[(self.row,self.col)]
        self.wood += 5*2**(res.size-1)
        del Resource.placed[(self.row,self.col)]
        d.drawAll.pop(d.drawAll.index(res))
        index = Forester.beingCollected.index(res)
        Forester.beingCollected.pop(index)

    def plant(self,d):
        self.idle = False
        newTree = Tree(self.row,self.col,d)
        newTree.anew(d)
        Resource.placeThing(newTree,self.row,self.col,d)
        self.state = 'idle'
        Forester.beingPlanted.remove((self.row,self.col))
        self.findWayOut(d)

    def plantCite(self,d):
        cites = []
        for (R,C) in self.cite.coverage:
            if (R,C) in Resource.placed: continue
            if d.gameMap[R][C] != 'land': continue
            surround = 0
            skip = False
            for drow in  range(-1,2):
                for dcol in range(-1,2):
                    if d.gameMap[R+drow][C+dcol] == 'build': skip = True
                    if drow == dcol == 0: continue
                    if (R+drow,C+dcol) in Resource.placed: surround += 1
            if surround >= 2 or skip: continue
            cites.append((R,C))
        return cites

class Farmer(Villager):
    pop = []
    beingCollected = [] # (R,C)
    beingPlanted = [] # (R,C)
    beingPruned = []

    def _init_(self,d):
        if len(Farmer.pop) == 0:
            Farmer.beingCollected=[]
            Farmer.beingPlanted=[]
        self.name = 'farmer ' + str(len(Forester.pop))
        self.state = 'idle'; self.idle = True
        self.queue = []; self.dir = ''
        self.nextX,self.nextY =(Villager.centerAbsXY(self.row,self.col,d))
        self.arrived = True; self.moving = True
        self.fieldSize = self.cite.rows * self.cite.cols
        self.updateDraw(d)
        Farmer.pop.append(self); self.job = 'Farmer'

    def action(self,d):
        if self.home != None:
            if self.foodAction(d): return
        if self.state == 'idle':
            if self.empty():
                self.moveToPlot(d)
            elif not self.oneMature():
                self.moveToPrune(d)
            else: self.moveToHarvest(d)
        elif self.state == 'plant' and self.arrived:
            if not self.wait: Villager.wait(self,10000); return
            elif self.waited < 3000: self.moving = False;return
            self.wait=self.waited = 0
            self.plant(d)
        elif self.state == 'prune' and self.arrived:
            if not self.wait: Villager.wait(self,10000); return
            elif self.waited < 3000: self.moving = False;return
            self.wait=self.waited = 0
            self.prune(d)
        elif self.state == 'harvest' and self.arrived:
            if not self.wait: Villager.wait(self,10000); return
            elif self.waited < 3000: self.moving = False;return
            self.wait=self.waited = 0
            self.harvest(d)
            if self.food >= 100:
                self.goToBarn(d)
                self.state = 'barn'
            elif not self.oneMature():
                if self.allEmpty(d): self.state = 'idle'
                else: self.moveToPrune(d)
            else: self.moveToHarvest(d)
        elif self.state == 'barn' and self.arrived:
            self.dropRes(d)

    def dropRes(self,d):
        self.barn.food += self.food
        self.food = 0
        self.idle = True; self.state = 'idle'

    def allEmpty(self,d):
        return len(self.cite.empty) == self.fieldSize

    def empty(self):
        return len(self.cite.empty) != 0

    def moveToPlot(self,d):
        (R,C) = self.cite.empty.pop() # auto made
        Farmer.beingPlanted.append((R,C))
        self.idle = self.arrived = False; self.moving = True
        self.state = 'plant'
        self.move(R,C,Maze,d)

    def oneMature(self):
        prunes = []
        for wheat in self.cite.wheat:
            if wheat.size >= 3:
                if not (wheat.R,wheat.C) in Farmer.beingCollected:
                    Farmer.beingCollected.append((wheat.R,wheat.C))
                    return True
        for wheat in self.cite.wheat:
            if wheat.size < 3:
                if not (wheat.R,wheat.C) in Farmer.beingPruned:
                    prunes.append((wheat.R,wheat.C))
        if prunes!=[]:
            Farmer.beingPruned.append(prunes[random.randint(0,len(prunes)-1)])
        return False

    def moveToHarvest(self,d):
        self.idle = self.arrived = False; self.state = 'harvest'
        (R,C) = Farmer.beingCollected[-1]; self.moving = True
        self.move(R,C,Maze,d)

    def plant(self,d):
        Farmer.beingPlanted.pop(Farmer.beingPlanted.index((self.row,self.col)))
        wheat = Wheat(self.cite,self.row,self.col,d)
        self.cite.wheat.add(wheat)
        wheat.place(self.row,self.col,d)
        self.idle=True; self.state = 'idle'
        self.arrive = False

    def moveToPrune(self,d):
        self.idle = self.arrived = False; self.state = 'prune'
        (R,C) = Farmer.beingPruned[-1]; self.moving = True
        self.move(R,C,Maze,d)

    def prune(self,d):
        Farmer.beingPruned.pop(Farmer.beingPruned.index((self.row,self.col)))
        for wheat in self.cite.wheat:
            if (self.row,self.col) == (wheat.R, wheat.C):
                wheat.size += 0.3
                wheat.update(d)
                self.idle = True; self.state = 'idle'
                return

    def harvest(self,d):
        Farmer.beingCollected.pop(Farmer.beingCollected.index((self.row,self.col)))
        for wheat in self.cite.wheat:
            if (self.row,self.col) == (wheat.R, wheat.C):
                self.food += 15*2**(int(wheat.size)-1)
                d.drawAll.pop(d.drawAll.index(wheat))
                self.cite.wheat.remove(wheat)
                self.cite.empty.append((self.row,self.col))
                return

class Gatherer(Villager):
    pop =[]

    def _init_(self,d):
        # if len(Farmer.pop) == 0:
        #     Farmer.beingCollected=[]
        #     Farmer.beingPlanted=[]
        self.name = 'gatherer ' + str(len(Gatherer.pop))
        self.state = 'idle'; self.idle = True
        self.queue = []; self.dir = ''
        self.nextX,self.nextY =(Villager.centerAbsXY(self.row,self.col,d))
        self.arrived = True; self.moving = True
        self.updateDraw(d)
        Gatherer.pop.append(self); self.job = 'Gatherer'

    def action(self,d):
        if self.home != None:
            if self.foodAction(d): return
        if self.state == 'idle':
            self.walkToFood(d)
            self.state = 'gather'
        elif self.state == 'gather' and self.arrived:
            if not self.wait: Villager.wait(self,10000); return
            elif self.waited < 3000: self.moving = False;return
            self.wait=self.waited = 0
            self.collectFood(d)
            if self.food >= 30:
                self.state = 'barn'
                self.goToBarn(d)
            else: self.state = 'idle'
        elif self.state == 'barn' and self.arrived:
            self.dropRes(d)
            self.state = 'idle'

    def collectFood(self,d):
        trees = 0
        for (R,C) in self.cite.coverage:
            if d.gameMap[R][C] == 'tree':
                trees += 1
        plus = (trees/9)//0.1/10
        if plus >= 3: plus = 3
        self.food += plus

    def walkToFood(self,d):
        self.moving = True; options = []
        self.arrived = self.idle = False
        for (R,C) in self.cite.coverage:
            if d.gameMap[R][C] == 'land':
                options.append((R,C))
        (R,C) = options[random.randint(0,len(options)-1)]
        self.arrived = self.idle = False
        self.move(R,C,Maze,d)
        return

    def dropRes(self,d):
        self.barn.food += self.food
        self.food = 0
        self.idle = True; self.state = 'idle'; self.idle = True


class Builder(Villager):
    pop = []

    def _init_(self,d):
        if len(Builder.pop) == 0:
            self.cite.beingMoved=[0,0]
        self.name = 'builder ' + str(len(Builder.pop))
        self.state = 'idle'; self.idle = True
        self.queue = []; self.dir = ''
        self.nextX,self.nextY =(Villager.centerAbsXY(self.row,self.col,d))
        self.arrived = True; self.moving = True
        self.updateDraw(d)
        Builder.pop.append(self); self.job = 'Builder'
        self.citeSurrounding(d)

    def citeSurrounding(self,d):
        R3,C3 = self.cite.BR_Row, self.cite.BR_Col
        rows,cols = self.cite.rows, self.cite.cols
        R4=R3; C2=C3
        R2=R1=R3-(rows-1); C1=C4=C3-(cols-1)
        self.sur = []
        for dcol in range(cols):
            self.sur.append((R1-1,C1+dcol))
            self.sur.append((R4+1,C4+dcol))
        for drow in range(rows):
            self.sur.append((R1+drow,C1-1))
            self.sur.append((R3+drow,C2+1))

    def action(self,d):
        if self.home != None:
            if self.foodAction(d): return
        if self.state == 'idle':
            self.reqRes = self.neededRes()
            if self.reqRes != [0,0]:
                self.goToBarn(d)
            else:
                self.state = 'build'
        elif self.state == 'barn' and self.arrived:
            self.getRes(d)
            self.state = 'transport'
            self.goToCite(d)
        elif self.state == 'transport' and self.arrived:
            self.dropRes(d)
        elif self.state == 'build':
            if not self.arrived:
                self.goToCite(d)
            else:
                if not self.wait: Villager.wait(self,10000); return
                elif self.waited < 3000: self.moving = False;return
                self.wait=self.waited = 0
                try:
                    self.build(d)
                    self.goToCite(d)
                except: self.state = 'idle'; return

    def neededRes(self):
        cite = self.cite
        neededWood=cite.buildWood[1]-cite.buildWood[0]-cite.beingMoved[0]
        neededStone=cite.buildStone[1]-cite.buildStone[0]-cite.beingMoved[1]
        if neededWood>20: neededWood = 20
        elif neededWood<0: neededWood = 0
        if neededStone>20: neededStone = 20
        elif neededStone<0: neededStone=0
        cite.beingMoved[0] += neededWood
        cite.beingMoved[1] += neededStone
        return [neededWood,neededStone]

    def build(self,d):
        if self.cite.built: self.state = 'idle'; return
        self.cite.completion += 10
        self.checkComplete(d)

    def checkComplete(self,d):
        if self.cite.completion >= 100:
            self.cite.built = True
            self.cite.workers = []
            cite = self.cite
            reassignJobs(self.cite,d)
            if isinstance(cite,House):
                cite.moveIn(d)
                House.placed.append(cite)
            cite.worker = 0

    def dropRes(self,d):
        diff = self.cite.buildStone[1]-self.cite.buildStone[0]-self.stone
        if diff < 0:
            self.cite.buildStone[0]=self.cite.buildStone[1]
            self.barn.stone += -diff
            self.stone = 0
        diff = self.cite.buildWood[1]-self.cite.buildWood[0]-self.wood
        if diff<0:
            self.cite.buildWood[0]=self.cite.buildWood[1]
            self.barn.wood += self.wood
            self.wood = 0
        Resource.deducted[0] -= self.wood
        Resource.deducted[1] -= self.stone
        self.cite.beingMoved[0] -= self.wood
        self.cite.beingMoved[1] -= self.stone
        self.cite.buildStone[0] += self.stone; self.stone = 0
        self.cite.buildWood[0] += self.wood; self.wood = 0
        self.state = 'idle'; self.idle = True

    def goToCite(self,d):
        options = []
        self.idle = self.arrived = False
        for (R,C) in self.sur:
            if d.gameMap[R][C] == 'land':
                options.append((R,C))
        option = random.randint(0,len(options)-1)
        (R,C) = options[option]
        self.move(R,C,Maze,d)

    def getRes(self,d):
        [reqWood, reqStone] = self.reqRes
        dwood = dstone = 0
        if reqWood>0:
            if self.barn.wood>0:
                if self.barn.wood>reqWood:
                    if reqWood <= 20: dwood = reqWood
                    else: dwood = 20
                else:
                    if self.barn.wood <= 20: d.wood=self.barn.wood
                    else: dwood=20
        if reqStone>0:
            if self.barn.stone>0:
                if self.barn.stone>reqStone:
                    if reqStone <= 20: dstone = reqStone
                    else: dstone = 20
                else:
                    if self.barn.stone <= 20: d.stone=self.barn.stone
                    else: dstone=20
        self.wood+=dwood; self.stone += dstone
        self.barn.stone-=dstone; self.barn.wood-=dwood
        self.barn.beingTaken[0]-=dwood;self.barn.beingTaken[1]-=dstone
        # self.cite.beingMoved[0]+=dwood;self.cite.beingMoved[1]+=dstone

    def goToBarn(self,d):
        [wood, stone] = self.reqRes
        self.arrived = self.idle = False
        shortest = 1000; trgR=trgC=None
        item = None
        if Building.placed == []: self.idle = True; return
        for build in Building.placed:
            if isinstance(build,Barn):
                remainStone = build.wood - build.beingTaken[0]
                remainStone = build.stone - build.beingTaken[1]
                if (remainStone != 0 and wood) != 0 or \
                    (remainStone !=0 and stone !=0):
                    (row,col) = build.BR_Row+1, build.BR_Col+1
                    dis = abs(row-self.row)+abs(col-self.col)
                    if dis<shortest:
                        shortest = dis
                        self.barn = build
                        for dcol in range(build.cols):
                            if d.gameMap[row+1][col-dcol] == 'land':
                                (trgR,trgC) = (row+1,col-dcol)
        if shortest == 1000: self.idle = True; return
        self.state = 'barn'
        self.move(trgR,trgC,Maze,d)

def renumber(popList):
    for i in range(len(popList)):
        vil = popList[i]
        if str(i+1) not in vil.name:
            for j in range(i,len(popList)):
                A = popList[j].name.split(' ')
                popList[j].name = A[0] + ' ' + str(j+1)
            return

def changeJobs(d):
    if d.oldJob == 'laborer':
        for vil in Villager.pop:
            if 'laborer' in vil.name:
                # select closest
                Laborer.beingCollected.discard((vil.removeR,vil.removeC))
                Laborer.pop.pop(Laborer.pop.index(vil))
                renumber(Laborer.pop)
                vil.cite = d.newCite
                if not d.newCite=='builder':
                    vil.cite.workers.append(vil.realName)
                if d.newJob == 'forester':
                    vil.__class__ = Forester
                    vil._init_(d)
                    renumber(Forester.pop)
                elif d.newJob == 'farmer':
                    vil.__class__ = Farmer
                    vil._init_(d)
                    renumber(Farmer.pop)
                elif d.newJob == 'gatherer':
                    vil.__class__ = Gatherer
                    vil._init_(d)
                elif d.newJob == 'builder':
                    vil.__class__ = Builder
                    vil._init_(d)
                    renumber(Builder.pop)
                d.laborers -= 1
                return
    elif d.newJob == 'laborer':
        for vil in Villager.pop:
            if d.oldJob in vil.name:
                # selesct closest
                if not d.oldJob == 'builder':
                    vil.cite.workers.pop(vil.cite.workers.index(vil.realName))
                if d.oldJob == 'forester':
                    Forester.pop.pop(Forester.pop.index(vil))
                    renumber(Forester.pop)
                elif d.oldJob == 'farmer':
                    Farmer.pop.pop(Farmer.pop.index(vil))
                    renumber(Farmer.pop)
                elif d.oldJob == 'gatherer':
                    Gatherer.pop.pop(Gatherer.pop.index(vil))
                    renumber(Gatherer.pop)
                elif d.oldJob == 'builder':
                    vil.cite.beingMoved[0] -= vil.reqRes[0]
                    vil.cite.beingMoved[1] -= vil.reqRes[1]
                    Builder.pop.pop(Builder.pop.index(vil))
                    renumber(Builder.pop)
                vil.__class__ = Laborer
                vil._init_(d)
                renumber(Laborer.pop)
                vil.cite = None
                d.laborers += 1
                return

def findMalesAndFemales(house):
    males=[]; females = []
    for vil in Villager.pop:
        if vil.age>=Villager.adulthood and vil.home==house:
            if vil.gender=='m':males.append(vil)
            else: females.append(vil)
    return (males,females)

def rearrangeHousing(d):
    least = 4; leastHouse = None
    for house in House.placed:
        if house.adults <= least:
            leastHouse = house; least = house.adults
    for house in House.placed:
        done = False
        if house.adults >= leastHouse.adults + 2:
            (males,females) = findMalesAndFemales(house)
            if house.males > 1:
                person = males.pop()
                person.kickOut()
                person.newHouse(leastHouse)
                done = True
            if house.females > 1:
                person = females.pop()
                person.kickOut()
                person.newHouse(leastHouse)
                done = True
        if done: break
    for house in House.placed:
        if house.adults == 0:
            for anoHouse in House.placed:
                (males,females) = findMalesAndFemales(anoHouse)
                if anoHouse.males > 1:
                    person = males.pop()
                    person.kickOut()
                    person.newHouse(house)
                if anoHouse.females > 1:
                    person = females.pop()
                    person.kickOut()
                    person.newHouse(house)
    # single person in a house
    for house in House.placed:
        found = False
        if house.adults == 1:
            onlyGen = 'm' if house.males == 1 else 'f'
            neededGen = 'm' if onlyGen == 'f' else 'f'
            (males,females) = findMalesAndFemales(house)
            if onlyGen == 'm':
                loner = males.pop()
            elif onlyGen == 'f':
                loner = females.pop()
            for anoHouse in House.placed:
                if anoHouse != house:
                    if neededGen == 'm':
                        if anoHouse.males > 1:
                            (males,a) = findMalesAndFemales(anoHouse)
                            match = males.pop()
                            match.kickOut()
                            match.newHouse(house)
                            found = True
                    elif neededGen == 'f':
                        if anoHouse.females > 1:
                            (a,females)=findMalesAndFemales(anoHouse)
                            match = females.pop()
                            match.kickOut()
                            match.newHouse(house)
                            found = True
                if found: break
            if found: break
    # two house with single gender
    for house in House.placed:
        if house.males >= 2 and house.females<2:
            maleHouse = house
            (males,unimportant) = findMalesAndFemales(maleHouse)
            for anoHouse in House.placed:
                if anoHouse.females >= 2 and anoHouse != maleHouse:
                    (unimportant,females) = findMalesAndFemales(anoHouse)
                    man = males.pop()
                    woman = females.pop()
                    man.kickOut(); woman.kickOut()
                    man.newHouse(anoHouse); woman.newHouse(maleHouse)
                    return

def moveIn(d):
    for vil in Villager.pop:
        if len(d.newHouse.occupants) >= 4: rearrangeHousing(d); return
        if vil.home == None:
            vil.home = d.newHouse
            d.newHouse.occupants[vil.realName] = vil.age
            if vil.age >= Villager.adulthood:
                d.newHouse.adults += 1
                if vil.gender == 'm': d.newHouse.males += 1
                else: d.newHouse.females += 1
    rearrangeHousing(d)

def checkClicked(R,C,d):
    for vil in Villager.pop:
        if (vil.row,vil.col) == (R,C):
            d.clickedVil = vil
            return True
    return False

def newBabies(d):
    import Buttons
    for vil in Villager.pop:
        vil.age += 0.4
        if isinstance(vil,Baby) and vil.age >= Villager.adulthood:
            d.flag = [vil]; Buttons.processFlag(d)
            Villager.babies -= 1
            if vil.gender=='m':
                Villager.males += 1
            elif vil.gender=='f':
                Villager.females += 1
            renumber(Baby.pop)
            vil.__class__ = Laborer
            vil._init_(d)
            renumber(Laborer.pop)
        try:vil.home.occupants[vil.realName] = vil.age
        except: pass
    # new babies
    rearrangeHousing(d)
    for house in House.placed:
        if house.males == 1 and house.females == 1 and len(house.occupants)<4:
            gender = ['m','f'][random.randint(0,1)]
            newBorn = Baby(gender,d,0)
            d.flag = newBorn; Buttons.processFlag(d)
            newBorn.newHouse(house)

def dead(d):
    import Buttons
    for vil in Villager.pop:
        if vil.hunger >= 120:
            d.flag = vil;Buttons.processFlag(d)
            if isinstance(vil,Baby): Villager.babies -= 1
            elif vil.gender=='m': Villager.males-=1
            elif vil.gender=='f': Villager.females-=1
            if vil.home != None: vil.kickOut()
            if isinstance(vil,Laborer):
                Laborer.pop.pop(Laborer.pop.index(vil))
                renumber(Laborer.pop)
            elif isinstance(vil,Forester):
                Forester.pop.pop(Forester.pop.index(vil))
                renumber(Forester.pop)
            elif isinstance(vil,Baby):
                Baby.pop.pop(Baby.pop.index(vil))
                renumber(Baby.pop)
            elif isinstance(vil,Gatherer):
                Gatherer.pop.pop(Gatherer.pop.index(vil))
                renumber(Gatherer.pop)
            elif isinstance(vil,Farmer):
                Farmer.pop.pop(Farmer.pop.index(vil))
                renumber(Farmer.pop)
            elif isinstance(vil,Builder):
                vil.cite.beingMoved[0] -= vil.reqRes[0]
                vil.cite.beingMoved[1] -= vil.reqRes[1]
                Builder.pop.pop(Builder.pop.index(vil))
                renumber(Builder.pop)
            Villager.pop.pop(Villager.pop.index(vil))
            d.drawAll.pop(d.drawAll.index(vil))
            rearrangeHousing(d)
            return

def findIdle():
    Villager.idle = 0
    for vil in Villager.pop:
        if (not isinstance(vil,Baby)) and vil.state == 'idle':
            Villager.idle += 1
