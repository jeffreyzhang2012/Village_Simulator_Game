import pygame,random, math
from Buildings import Barn
import Buildings
from Buildings import Building
from Buildings import Farm

class Resource(pygame.sprite.Sprite):
    placed = dict() # (R,C):'name'
    cross = pygame.image.load('resources/cross.png')
    a,b,crossWid, crossHei = cross.get_rect()
    marked = set()
    stone = 0
    wood = 0
    food = 0
    deducted = [0,0,0] # wood, stone ,food

    def __init__(self):
        self.image = self.image.convert_alpha()
        self.marked = False

    def draw(self,screen,d):
        X, Y = self.absImageX - d.scrollX, self.absImageY - d.scrollY
        screen.blit(self.image,(X,Y))
        if self.marked:
            screen.blit(Resource.cross,(self.absX3-d.scrollX-Resource.crossWid/2,\
                    self.absY3-d.scrollY-Resource.crossHei/2))

    def findAbsXYWithRowCol(row,col,d):
        # returns the bottom-right vertice (3rd vertice)
        xShiftEachRow = math.tan(d.angle)*d.gridHei
        Y2 = row*d.gridHei; Y3 = Y2 + d.gridHei
        X1 = col*d.gridWid - Y2*math.tan(d.angle)
        X3 = X1 + d.gridWid - xShiftEachRow
        return X3,Y3

    def __repr__(self):
        return self.name + str(self.num)

    def placeThing(thing,BR_Row1, BR_Col1, d):
        Resource.placed[(BR_Row1,BR_Col1)] = thing
        if isinstance(thing,Stone):
            Stone.placed.append(thing); return
        for i in range(len(d.drawAll)):
            placed = d.drawAll[i]
            BRR2,BRC2=placed.BR_Row,placed.BR_Col;rows,cols=placed.rows,placed.cols
            R1=R2=BRR2-rows+1;R3=R4=BRR2;C1=C4=BRC2-cols+1;C2=C3=BRC2
            if R3 <= BR_Row1 - thing.rows: continue
            next = False
            for (R,C) in [(R1,C1),(R2,C2),(R3,C3),(R4,C4)]:
                if R < BR_Row1 and C <= BR_Col1: next = True; break
            if next: continue
            else:
                d.drawAll.insert(i,thing); return
                # updateMap(build,BR_Row1,BR_Col1,d); return
        d.drawAll.append(thing)

class Tree(Resource):
    placed = []
    num = 1
    images=[pygame.image.load('resources/tree %d%s.png'%(i,j))for i in range(1,4)\
                    for j in ['s','m','l']]
    tree1 = images[0:3]
    tree2 = images[3:6]
    tree3 = images[6:9]

    def __init__(self,R,C,d):
        self.BR_Row, self.BR_Col = R, C
        self.rows = self.cols = 1
        self.num = Tree.num
        Tree.num += 1
        self.name = 'tree'
        self.kind = str(random.randint(1,3))
        self.size = random.randint(1,3)
        self.time = random.randint(0,29999)
        self.image = eval('Tree.tree'+self.kind)[self.size-1]
        a,b,self.imageWid,self.imageHei = self.image.get_rect()
        self.absX3, self.absY3 = Resource.findAbsXYWithRowCol(R,C,d)
        self.absImageX = self.absX3 - self.imageWid/3
        self.absImageY = self.absY3 - self.imageHei/2
        Tree.placed.append(self)
        super().__init__()

    def anew(self,d):
        R,C = self.BR_Row, self.BR_Col
        self.size = 1
        self.time = 0
        self.image = eval('Tree.tree'+self.kind)[0]
        a,b,self.imageWid,self.imageHei = self.image.get_rect()
        self.absX3, self.absY3 = Resource.findAbsXYWithRowCol(R,C,d)
        self.absImageX = self.absX3 - self.imageWid/3
        self.absImageY = self.absY3 - self.imageHei/2

    def age(self,d):
        if self.size == 3: return
        self.size += 1
        self.image = eval('Tree.tree'+self.kind)[self.size-1]
        a,b,self.imageWid,self.imageHei = self.image.get_rect()
        self.absX3, self.absY3 = Resource.findAbsXYWithRowCol(self.BR_Row, \
            self.BR_Col,d)
        self.absImageX = self.absX3 - self.imageWid/3
        self.absImageY = self.absY3 - self.imageHei/2

class Stone(Resource):
    placed = []
    num = 1
    images = [pygame.image.load('resources/stone %d.png'%i)for i in range(1,4)]
    def __init__(self,R,C,d):
        self.BR_Row, self.BR_Col = R, C
        self.rows = self.cols = 1
        self.num = Stone.num
        Stone.num += 1
        self.name = 'stone'
        self.image = Stone.images[random.randint(0,2)]
        a,b,self.imageWid,self.imageHei = self.image.get_rect()
        self.absX3, self.absY3 = Resource.findAbsXYWithRowCol(R,C,d)
        self.absImageX = self.absX3 - self.imageWid/2
        self.absImageY = self.absY3 - self.imageHei/2
        super().__init__()

def generateOne(d,res,spread,density,seeds,gap,new):
    for i in range(seeds): # 20 seeds
        j, k = random.randint(0,d.rows-1),random.randint(0,d.cols-1)
        while d.gameMap[j][k] != 'land':
            j, k = random.randint(0,d.rows-1),random.randint(0,d.cols-1)
        d.gameMap[j][k] = res
        if res=='stone':
            Resource.placeThing(Stone(j,k,d),j,k,d)
        elif res == 'tree':
            item = Tree(j,k,d)
            Resource.placeThing(item,j,k,d)
            if new: item.anew(d)
        for drow in range(-1*spread,spread):
            for dcol in range(-1*spread,spread):
                if drow+j >= d.rows or dcol+k >= d.cols: continue
                prob = (1 - (abs(drow) + abs(dcol))/(spread*2)) - density
                if random.randint(0,100) <= prob* 100:
                    if d.gameMap[j+drow][k+dcol] == 'land':
                        near = []
                        for Drow in range(-gap,gap+1):
                            for Dcol in range(-gap,gap+1):
                                near.append(d.gameMap[j+drow+Drow][k+dcol+Dcol])
                        if res in near: continue
                        d.gameMap[j+drow][k+dcol] = res
                        if res == 'stone':
                            Resource.placeThing(Stone(j+drow,k+dcol,d),j+drow,k+dcol,d)
                        elif res == 'tree':
                            item = Tree(j+drow,k+dcol,d)
                            Resource.placeThing(item,j+drow,k+dcol,d)
                            if new: item.anew(d)

def generateRes(d):
    generateOne(d,'tree',30,0.8,16,2,False)
    generateOne(d,'stone',18,0.7,8,1,False)

def newTrees(d):
    generateOne(d,'tree',30,0.9,16,2, True)

def update(d):
    Resource.wood = Resource.stone = Resource.food = 0
    for barn in Barn.placed:
        Resource.wood += barn.wood
        Resource.wood -= Resource.deducted[0]
        Resource.stone += barn.stone
        Resource.stone -= Resource.deducted[1]
        Resource.food += barn.food
