import pygame, sys, math, random
from Buildings import Building
from Buildings import House
from Buildings import Hut
from Buildings import Barn
from Buildings import Forest
from Buildings import Farm
import Villagers
from Villagers import Villager, Laborer, Baby
from Resources import Resource
from Resources import Stone
from Resources import Tree
import Resources, Buttons
from Maze import Maze
from Buttons import Button
from Buttons import clearButton
from Buildings import Wheat

def init(d):
    d.mode='start'
    d.placed = dict()
    d.drawAll = []
    d.imageLib={}
    d.width=1200;d.height=900
    d.pause = False; d.tick = 20; d.speed = 2
    d.done=False
    d.lastClick = 0
    d.margin=30 #scroll beyond margin

def getImage(d,path):
    image = d.imageLib.get(path)
    if image == None:
        image=pygame.image.load(path)
        d.imageLib[path]=image
    return image

def startMenuInit(d):
    d.back = pygame.image.load('back.png')
    d.backWid,d.backHei = d.back.get_width(), d.back.get_height()
    d.background = pygame.image.load('Capture backup.png')
    d.story = pygame.image.load('story.png')
    d.storyWid,d.storyHei = d.story.get_width(), d.story.get_height()
    d.help = pygame.image.load('help.png')
    d.start_boxWid=d.width*0.2
    d.start_boxHei=d.start_boxWid*0.2
    d.start_boxes=['New Game','Story','Help']
    d.start_boxColors=[(100,100,100)]*len(d.start_boxes)
    d.start_boxGap=d.start_boxHei*2
    d.start_boxPos = [[0,0]for i in range(len(d.start_boxes))]
    for i in range(len(d.start_boxes)):
        d.start_boxPos[i][0]=d.width*0.5
        d.start_boxPos[i][1]=d.height*0.2+d.start_boxGap*i

def gameInit(d):
    box=getImage(d,'box.png')
    a,b,d.gridWid,d.gridHei=d.imageLib['box.png'].get_rect()
    # a and b are usless, just the x, y values of top left
    d.angle=25*math.pi/180
    d.fullX=d.fullY=3000
    d.scrollX,d.scrollY=int(d.fullX/2-0.5*d.width),int(d.fullY/2-0.5*d.height)
    #absolute coordinate of top-left corner
    gridInit(d)
    # BuildingInit(d)
    mapGeneration(d)
    Buttons.buttonInit(d)
    startGameInit(d)
    resourceInit(d)
    d.laborers = len(Laborer.pop)
    d.hoveringValid = False
    d.hovering = False
    d.hoveringBR_Row = d.hoveringBR_Col = 0; d.clickedBuild = None
    d.farmHovering = False; d.hovFarm = None; d.farmReady = False
    d.clearReady = False; d.clearing = False
    d.manageVil = False; d.moveInVils = False; d.newHouse = None
    d.clickedVil = None; d.flag = None
    d.tab = pygame.image.load('tabs/resource.png')
    a,b,d.tabWid,d.tabHei = d.tab.get_rect()
    tabR, tabC = 5,2
    d.tabDx, d.tabDy = d.tabWid/tabC, d.tabHei/tabR

def drawTab(screen,d):
    screen.blit(d.tab,(0,0))
    text1 = [Resource.wood,Resource.stone,Resource.food,len(Laborer.pop)]
    for i in range(len(text1)):
        cy = (i+1.5)*d.tabDy
        text=str(text1[i]) if text1[i]>0 else '0'
        if i == 3: text+=' / %d'%(Villager.males+Villager.females)
        Building.drawText(screen,str(text),15,40,cy)
    text2 = [Villager.males,Villager.females,Villager.idle,Villager.babies]
    for i in range(len(text2)):
        cy = (i+1.5)*d.tabDy
        Building.drawText(screen,str(text2[i]),15,70+d.tabDx,cy)

def startGameInit(d):
    barn = Barn()
    barn.BR_Row,barn.BR_Col = 60,60
    barn.wood = barn.stone = 1000
    barn.food = 2000
    barn.built = True
    placeBuilding(barn,110,110,d)
    d.v1 = Laborer('m',d,32)
    d.v2 = Laborer('f',d,18)
    d.v3 = Laborer('f',d,10)
    d.v4 = Laborer('m',d,62)
    d.v5 = Baby('m',d,0)
    d.v6 = Baby('f',d,4)
    d.v6 = Laborer('m',d,6)
    d.v7 = Laborer('m',d,6)
    d.v8 = Laborer('m',d,0)
    d.v9 = Laborer('f',d,6)
    d.v10 = Baby('m',d,4)
    d.v11 = Laborer('f',d,6)
    d.v22 = Laborer('f',d,4)
    d.v33 = Laborer('f',d,6)
    # d.v44 = Laborer('f',d,6)
    # d.v55 = Laborer('f',d,6)
    d.threeSec = 0
    d.oneSec = 0
    d.thirtySec = 0
    d.time = 0

def resourceInit(d):
    Resources.generateRes(d)

def drawTabs(screen,d):
    if d.clickedBuild != None:
        d.clickedBuild.drawTab(screen,d)

def storyDraw(screen,d):
    x=d.width/2-d.storyWid/2
    screen.blit(d.story,(x,0))
    screen.blit(d.back,(0,0))

def helpDraw(screen,d):
    x=d.width/2-d.storyWid/2
    screen.blit(d.help,(x,0))
    screen.blit(d.back,(0,0))

def helpEvents(screen,d):
    if pygame.mouse.get_pressed()[0]:
        x,y=pygame.mouse.get_pos()
        if 0<=x<=d.backWid and 0<=y<=d.backHei:
            d.mode = 'start'

def gameDraw(screen,d):
    screen.fill((0,0,0))
    drawMap(screen,d)
    # drawGrid(screen,d)
    drawPlacedObjects(screen,d,Building,Villager)
    Buttons.drawButtons(screen,d)
    drawTabs(screen,d)
    if d.hovering:
        drawHighlightedGrid(screen,d)
        hoverBuilding(d.hoveringBuild,screen,d)
    elif d.farmHovering:
        hoverFarm(screen,d)
    elif d.clearing:
        hoverClear(screen,d)
    elif d.clickedVil != None:
        d.clickedVil.drawTab(screen,d)
    drawTab(screen,d)
    if d.flag!=None: drawFlag(screen,d)

def drawFlag(screen,d):
    cx = d.width/2; cy = d.height*0.1
    drawText(screen,d.flagText,30,cx,cy)

def rightClick(d):
    d.clickedBuild = None
    d.hovering = False; d.hoveringBuild = None; d.hovFarm = None
    d.farmReady = False ; d.farmHovering = False
    d.clearing = False; Button.clear = None
    for but in d.Buttons:
        but.clicked = False

def mouseClick(d):
    x,y=pygame.mouse.get_pos()
    row,col = findGridRowColInParallel(x,y,d)
    if d.clickedBuild != None:
        if (not d.clickedBuild.built) and (d.clickedBuild.tabX<x<d.clickedBuild.tabX\
            +Building.notBuiltWid and d.clickedBuild.tabY<y<d.clickedBuild.tabY+\
            Building.notBuiltHei):
                d.clickedBuild.clickButton(x,y,d);d.clickedVil=None
        elif d.clickedBuild.built and (d.clickedBuild.tabX<x<d.clickedBuild.tabX+\
            d.clickedBuild.tabWid and d.clickedBuild.tabY<y<d.clickedBuild.tabY+\
            d.clickedBuild.tabHei):
            d.clickedBuild.clickButton(x,y,d); d.clickedVil = None
        else: d.clickedBuild = None
    elif Buttons.checkButtons(x,y,d): d.clickedVil = None
    elif d.farmReady:
        d.farmHovering = True; d.farmReady = False; d.clickedVil = None
        d.hovFarm = Farm()
        d.hovFarm.anchorR, d.hovFarm.anchorC = row, col
        d.hovFarm.hover = True
    elif d.clearReady:
        d.clearing = True
        d.clearAnchorR, d.clearAnchorC = row, col; d.clearReady = False
    elif Button.clear != None: # clearing
        d.clearR,d.clearC = row, col
        Buttons.clear(d)
        Button.clear = None; d.clearing = False
    elif d.farmHovering and d.hoveringValid:
        d.hovFarm.rows=abs(d.hovFarm.rows); d.hovFarm.cols=abs(d.hovFarm.cols)
        placeBuilding(d.hovFarm,d.hovFarm.BR_Row,d.hovFarm.BR_Col,d)
        d.hovring = False; d.farmHovering=False;d.hovFarm = None
    elif d.hovering and d.hoveringValid:
        placeBuilding(d.hoveringBuild,d.hoveringBR_Row,d.hoveringBR_Col,d)
        d.hovering = False
    elif Villagers.checkClicked(row,col,d): return
    elif Building.checkClicked(row,col,d): return
    else: d.clickedBuild = None; d.clickedVil = None

def gameEvents(event,d):
    if d.manageVil: manageVil(d)
    scrollScreen(d)
    if pygame.mouse.get_pressed()[2]:
        rightClick(d)
    elif pygame.mouse.get_pressed()[0]:
        mouseClick(d)
    if pressed('r') and d.hovering == True:
        d.hoveringBuild.rotate()
    if pressed('h'):
        d.hovering = True
        d.hoveringBuild = House()
    elif pressed('g'):
        d.hovering = True
        d.hoveringBuild = Hunt()
    elif pressed('f'):
        d.hovering = True
        d.hoveringBuild = Forest()
    elif pressed('z'):
        d.v1.move(92,96,Maze,d)
    elif pressed('x'):
        d.v1.move(80,81,Maze,d)
    elif pressed('q'):
        print(d.hoveringBuild.name)
    return

def manageVil(d):
    d.manageVil = False
    Villagers.changeJobs(d)
    d.laborers = len(Laborer.pop)

def gridInit(d):
    d.gridPos = [] # a 3d list containing each row, the parallelograms of each
    # row, and the four coordinates of each parallelogram
    xShiftEachRow = math.tan(d.angle)*d.gridHei
    X1 = 0; Y1 = 0
    X2=X1+d.gridWid; Y2 = Y1
    X4=X1-xShiftEachRow; Y4 = Y2 + d.gridHei
    X3=X4+d.gridWid; Y3 = Y4 # 1-top left 2-top right 3-bottom right 4-bottom le
    row = 0
    while Y1<=d.fullY:
        startX3=X3 # the first parallelogram, for reference next row
        rowList = []
        col = 0
        while X4 <= d.fullX:#leftmost point
            # while X2<=0:#the rightmost point
            #     X1+=d.gridWid;X2+=d.gridWid;X3+=d.gridWid;X4+=d.gridWid
            if X2 >= 0:
                rowList.append([(X1,Y1),(X2,Y2),(X3,Y3),(X4,Y4),(row,col)])
            col += 1
            X1+=d.gridWid;X2+=d.gridWid;X3+=d.gridWid;X4+=d.gridWid
        d.gridPos.append(rowList)
        Y1+=d.gridHei;Y2+=d.gridHei;Y3+=d.gridHei;Y4+=d.gridHei;
        X2=startX3;X1=X2-d.gridWid;X3=X2-xShiftEachRow;X4=X3-d.gridWid
        row += 1
    d.rows,d.cols = row+1,col+1

def probability(percentage): # integer
    randomNum = random.randint(0,99)
    if randomNum in range(percentage): return True
    return False

def isSea(d,row,col):
    distance = abs(row-d.centerRow)+abs(col-d.centerCol)
    fullDistance = d.centerRow
    x = distance/fullDistance
    percentage = round((x**4 - 0.01*random.randint(0,10))*100) # this function generates the ideal terrain
    return probability(percentage)

def adjacentToLand(d,row,col):
    gameMap = d.gameMap
    for drow in [-1,0,1]:
        for dcol in [-1,0,1]:
            if drow*dcol != 0: continue
            if row+drow >= d.rows or col+dcol >= d.cols: return
            if gameMap[row+drow][col+dcol]=='land': return True
    return False

def makeLand(d,row,col):
    if adjacentToLand(d,row,col):
        if not isSea(d,row,col):
            d.gameMap[row][col]='land'

def fillHoles(d):
    for row in range(len(d.gameMap)):
        if 'land' in d.gameMap[row]:
            hole = False
            for col in range(len(d.gameMap[row])):
                if d.gameMap[row][col] == 'sea':
                    if hole == True: hole = False
                    else: hole = True # if next one is land, fill that cell with land
                else:
                    if hole: d.gameMap[row][col-1] = 'land'; hole = False
    for col in range(len(d.gameMap[0])):
        hole = False
        for row in range(len(d.gameMap)):
            if d.gameMap[row][col] == 'sea':
                if hole == True: hole = False
                else: hole = True # if next one is land, fill that cell with land
            else:
                if hole: d.gameMap[row-1][col] = 'land'; hole = False

def centerRowAndCol(d):
    topLeftRow, topLeftCol = d.gridPos[0][0][-1]
    bottomRightRow, bottomRightCol = d.gridPos[-1][-1][-1]
    d.centerCol = (bottomRightCol - topLeftCol)//2
    d.centerRow = (bottomRightRow - topLeftRow)//2

def mapGeneration(d):
    centerRowAndCol(d)
    rows, cols = d.rows, d.cols
    d.gameMap = [['sea']*cols for row in range(rows)]
    d.gameMap[d.centerRow][d.centerCol]='land'
    boxLen = 0 # how far it is from the centerbox
    while boxLen <= rows*0.9/2:
        boxLen += 1 # extends up, down, left, right by 1
        for col in range(d.centerCol-boxLen-1,d.centerCol+boxLen): #no corners yet
            for row in [d.centerRow-boxLen,d.centerRow+boxLen]:
                makeLand(d,row,col)
        for row in range(d.centerRow-boxLen+1,d.centerRow+boxLen):
            for col in [d.centerCol-boxLen,d.centerCol+boxLen]:
                makeLand(d,row,col)
        for (dirX,dirY) in {(-1,1),(1,1),(1,-1),(-1,-1)}: # make corners
            row,col = d.centerRow+dirY*boxLen, d.centerCol+dirX*boxLen
            makeLand(d,row,col)
    fillHoles(d)

def drawGrid(screen,d):
    startRow, endRow, startCol, endCol = drawLimit(d)
    # parallel coordinates
    for row in range(startRow,endRow+1):
        if row >= len(d.gridPos):continue
        for col in range(len(d.gridPos[row])):
            if col >= len(d.gridPos[row]):continue # prevent out of range
            points = d.gridPos[row][col]
            if points == None: continue
            [X1,X2,X3,X4]=[points[i][0]-d.scrollX for i in range(len(points)-1)]
            [Y1,Y2,Y3,Y4]=[points[i][1]-d.scrollY for i in range(len(points)-1)]
            point = [(X1,Y1),(X2,Y2),(X3,Y3),(X4,Y4)]
            pygame.draw.polygon(screen,(100,100,100),point,1)

def drawLimit(d):
    d.startR = d.scrollY//d.gridHei
    d.endR = d.startR + d.height//d.gridHei + 1
    d.startC = (d.scrollX+math.tan(d.angle)*d.scrollY)//d.gridWid
    screenCols = (d.width+math.tan(d.angle)*d.fullY)//d.gridWid + 1
    d.endC = d.startC + screenCols
    return d.startR, d.endR, d.startC, d.endC

def drawHighlightedGrid(screen,d):
    startRow, endRow, startCol, endCol = drawLimit(d)
    for placedBuilding in Building.drawAll:
        BR_Row, BR_Col= placedBuilding.BR_Row, placedBuilding.BR_Col
        rows, cols = placedBuilding.rows, placedBuilding.cols
        if BR_Row>=startRow and BR_Row-rows<=endRow \
          and BR_Col>= startCol and BR_Col - cols <= endCol:
              drawParallelogram(screen,d,rows,cols,BR_Row,BR_Col, 'Green',False)

def drawMap(screen,d):
    startRow, endRow, startCol, endCol = drawLimit(d)
    for row in range(d.rows):
        for col in range(d.cols):
            if startRow<=row<=endRow and startCol<=col<=endCol:
                if d.gameMap[row][col]=='sea':color = 'Blue'
                else: color = 'Green'
                drawParallelogram(screen,d,1,1,row,col,color,True)

def drawParallelogram(screen,d,rows,cols,BR_Row,BR_Col,color,solid):
    # the dimensions and bottom-right position of the parallelogram
    if solid: image = getImage(d,'solidParal%s.png'%color)
    else: image = getImage(d,'transparentParal%s.png'%color)
    # whether i'm drawing for a placed Building or hovering Building or invalid
    xShiftEachRow = math.tan(d.angle)*d.gridHei
    for i in range(rows):
        for j in range(cols):
            absX3,absY3 = findAbsXYWithRowCol(BR_Row-i,BR_Col-j,d)
            X3,Y3 = absX3 - d.scrollX, absY3 - d.scrollY
            imageX = X3 - d.gridWid
            imageY = Y3 - d.gridHei
            screen.blit(image,(imageX,imageY))

def mouse(d): # debug coordinate system
    x,y=pygame.mouse.get_pos()
    return findGridRowColInParallel(x,y,d)

def scrollScreen(d):
    mag = 17
    x,y = pygame.mouse.get_pos()
    if x<= d.margin:
        if not d.scrollX<=0: d.scrollX-=mag
        x = d.margin
        pygame.mouse.set_pos([x,y])
    elif x>=d.width-d.margin:
        if not d.scrollX+d.width>=d.fullX: d.scrollX+=mag
        x = d.width-d.margin
        pygame.mouse.set_pos([x,y])
    if y<= d.margin:
        if not d.scrollY<=0: d.scrollY-=mag
        y = d.margin
        pygame.mouse.set_pos([x,y])
    elif y>= d.height-d.margin:
        if not d.scrollY+d.height>=d.fullY: d.scrollY+=mag
        y = d.height-d.margin
        pygame.mouse.set_pos([x,y])
    drawLimit(d)

def mouseHover(build,d):
    row, col = mouse(d)
    if build.BR_Row-build.rows+1<= row <= build.BR_Row and \
        build.BR_Col-build.cols+1 <= col <= build.BR_Col:
        return True
    return False

def drawPlacedObjects(screen,d,Building,Villager):
    for farm in Farm.placed:
        if mouseHover(farm,d):
            farm.hover = True
        else:
            farm.hover = False
        farm.draw(screen,d)
    for stone in Stone.placed:
        stone.draw(screen,d)
    for thing in d.drawAll:
        if not d.startR-15<=thing.BR_Row<=d.endR+15 and \
            d.startC-7<=thing.BR_Col<=d.endC+7: continue
        if isinstance(thing,Building):
            if mouseHover(thing,d):
                thing.hover = True
            else:
                thing.hover = False
        thing.draw(screen,d)

def hoverClear(screen,d):
    R,C = mouse(d)
    lowR = max(d.clearAnchorR,R)
    lowC = max(d.clearAnchorC,C)
    rows,cols = abs(R-d.clearAnchorR)+1, abs(C-d.clearAnchorC)+1
    drawParallelogram(screen,d,rows,cols,lowR,lowC,'Yellow',False)

def hoverFarm(screen,d):
    R,C = mouse(d)
    anchorR, anchorC = d.hovFarm.anchorR, d.hovFarm.anchorC
    rows=anchorR-R
    if rows <0: rows -= 1
    else: rows += 1
    cols=anchorC-C
    if cols <0: cols -= 1
    else: cols += 1
    d.hovFarm.rows,d.hovFarm.cols = rows, cols
    d.hovFarm.drawHov(screen,d)
    d.hovFarm.BR_Row = max(anchorR,anchorR-rows-1)
    d.hovFarm.BR_Col = max(anchorC,anchorC-cols-1)
    rows,cols = abs(rows),abs(cols)
    validBuildPlace(d,d.hovFarm.BR_Row,d.hovFarm.BR_Col,rows,cols)
    color = 'Blue' if d.hoveringValid else 'Red'
    drawParallelogram(screen,d,rows,cols,d.hovFarm.BR_Row,\
        d.hovFarm.BR_Col,color,False)


def hoverBuilding(build,screen,d):
    # note: I put a transparent dot on the bottom right corner of each image
    # so that the distance from X0 to the bottom right corner of the bottom
    # right block is exactly half the image width, and same with Y0
    image = build.image
    a,b,imageWid,imageHei = image.get_rect()
    X,Y = pygame.mouse.get_pos()
    BR_X,BR_Y = X+imageWid/4, Y+imageHei/4   # the  bottom right corner of the
    # block on the bottom right
    if findGridRowColInParallel(BR_X,BR_Y,d) == None: return#mouse out of bounds
    BR_Row,BR_Col=findGridRowColInParallel(BR_X,BR_Y,d)
    d.hoveringBR_Row, d.hoveringBR_Col = BR_Row,BR_Col
    absX3, absY3 = findAbsXYWithRowCol(BR_Row, BR_Col, d)
    X3, Y3 = absX3 - d.scrollX, absY3 - d.scrollY
    build.imageX, build.imageY = X3 - imageWid/2, Y3 - imageHei/2
    build.BR_Row,build.BR_Col = BR_Row,BR_Col
    rows,cols = build.rows,build.cols
    validBuildPlace(d,BR_Row,BR_Col,rows,cols)
    color = 'Blue' if d.hoveringValid else 'Red'
    build.hover = True
    build.draw(screen,d)
    drawParallelogram(screen,d,rows,cols,BR_Row,BR_Col,color,False)

def validBuildPlace(d, BR_Row1, BR_Col1, rows1, cols1):
    for build in d.drawAll:
        if isinstance(build,Villager):continue
        BR_Row2, BR_Col2 = build.BR_Row, build.BR_Col
        rows2,cols2 = build.rows, build.cols
        for thing in [rows2,cols2, BR_Row2, BR_Col2]: thing += 1
            # must have at least one grid gap between each Building
        highest = min(BR_Row1-rows1, BR_Row2-rows2)
        lowest = max(BR_Row1, BR_Row2)
        leftest = min(BR_Col1-cols1, BR_Col2-cols2)
        rightest = max(BR_Col1, BR_Col2)
        if lowest-highest <= rows1+rows2 and rightest-leftest <= cols1+cols2:
            d.hoveringValid = False; return
    for build in Stone.placed:
        BR_Row2, BR_Col2 = build.BR_Row, build.BR_Col
        rows2,cols2 = build.rows, build.cols
        for thing in [rows2,cols2, BR_Row2, BR_Col2]: thing += 1
            # must have at least one grid gap between each Building
        highest = min(BR_Row1-rows1, BR_Row2-rows2)
        lowest = max(BR_Row1, BR_Row2)
        leftest = min(BR_Col1-cols1, BR_Col2-cols2)
        rightest = max(BR_Col1, BR_Col2)
        if lowest-highest <= rows1+rows2 and rightest-leftest <= cols1+cols2:
            d.hoveringValid = False; return
    for build in Farm.placed:
        BR_Row2, BR_Col2 = build.BR_Row, build.BR_Col
        rows2,cols2 = build.rows, build.cols
        for thing in [rows2,cols2, BR_Row2, BR_Col2]: thing += 1
            # must have at least one grid gap between each Building
        highest = min(BR_Row1-rows1, BR_Row2-rows2)
        lowest = max(BR_Row1, BR_Row2)
        leftest = min(BR_Col1-cols1, BR_Col2-cols2)
        rightest = max(BR_Col1, BR_Col2)
        if lowest-highest <= rows1+rows2 and rightest-leftest <= cols1+cols2:
            d.hoveringValid = False; return
    for drow in range(-1,rows1+1):
        for dcol in range(-1,cols1+1): # must be at least 1 tile away from sea
            if d.gameMap[BR_Row1-drow][BR_Col1-dcol]=='sea':
                d.hoveringValid = False; return
    d.hoveringValid = True

def placeThing(thing,BR_Row1, BR_Col1, d):
    if isinstance(thing,Farm): Farm.placed.append(thing); return
    for i in range(len(d.drawAll)):
        placed = d.drawAll[i]
        if isinstance(placed,Farm): continue
        BRR2,BRC2=placed.BR_Row,placed.BR_Col;rows,cols=placed.rows,placed.cols
        # if abs(placed.BR_Row-BR_Row1)+abs(placed.BR_Col-BR_Col1) >= 8: continue
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

def placeBuilding(build,BR_Row, BR_Col, d):
    try:BR_Row1, BR_Col1 = build.BR_Row, build.BR_Col
    except:  return
    if not build.name in Building.tally: Building.tally[build.name] = 1
    else: Building.tally[build.name] += 1
    if not (isinstance(build,Barn) and len(Barn.placed) == 1 ):
        Buttons.resDeduct(build,d)
    Building.placed.append(build)
    placeThing(build,BR_Row1,BR_Col1,d)
    updateMap(build,BR_Row1,BR_Col1,d)
    build.num = Building.tally[build.name]
    d.hoveringBuild = None; d.hovering = False
    if isinstance(build,Farm):
        build._init_(d)

def updateMap(build,BR_Row,BR_Col,d):
    (rows,cols) = (build.rows, build.cols)
    for drow in range(rows):
        for dcol in range(cols):
            if isinstance(build,Farm):d.gameMap[BR_Row-drow][BR_Col-dcol] = 'farm'
            else: d.gameMap[BR_Row-drow][BR_Col-dcol] = 'build'

def findAbsXYWithRowCol(row,col,d):
    # returns the bottom-right vertice (3rd vertice)
    xShiftEachRow = math.tan(d.angle)*d.gridHei
    Y2 = row*d.gridHei; Y3 = Y2 + d.gridHei
    X1 = col*d.gridWid - Y2*math.tan(d.angle)
    X3 = X1 + d.gridWid - xShiftEachRow
    return X3,Y3

def findGridRowColInParallel(X,Y,d):
    # used to move people and place objects in parallel coordinates
    absX,absY = d.scrollX + X, d.scrollY + Y
    row = int(absY//d.gridHei)
    col = int((absX + math.tan(d.angle)*absY)//d.gridWid)
    return row,col

def pressed(button):
    pressed=pygame.key.get_pressed()
    if pressed[eval('pygame.K_'+button)]:return True

def checkQuit(screen,d,event):
    if event.type == pygame.QUIT or pressed('ESCAPE'):
        d.done = True
        pygame.quit()
        pygame.display.quit()
        sys.exit()

def startMenuDraw(screen,d):
    wid, hei = d.start_boxWid, d.start_boxHei
    screen.blit(d.background,(0,0))
    for i in range(len(d.start_boxes)):
        cx,cy=d.start_boxPos[i][0],d.start_boxPos[i][1]
        drawCenteredRect(screen,d.start_boxColors[i],cx,cy,wid,hei)
        text=d.start_boxes[i]
        drawText(screen,text,20,cx,cy)

def startMenuEvents(d):
    pressed=False; button = None #which button is pressed
    if pygame.mouse.get_pressed()[0]: pressed=True
    x,y = pygame.mouse.get_pos()
    for i in range(len(d.start_boxes)):
        cx,cy=d.start_boxPos[i][0],d.start_boxPos[i][1]
        if inRect(cx,cy,d.start_boxWid,d.start_boxHei,x,y):
            d.start_boxColors[i]=(140,200,140)
            if pressed: button = d.start_boxes[i]
        else:
            d.start_boxColors[i]=(100,100,100)
    if button == 'New Game': d.mode='game'
    elif button =='Story': d.mode = 'story'
    elif button == 'Help': d.mode = 'help'

def inRect(cx,cy,wid,hei,mouseX,mouseY):
    # center of rectangle
    return cx-0.5*wid<=mouseX<=cx+0.5*wid and cy-0.5*hei<=mouseY<=cy+0.5*hei

def drawCenteredRect(screen,color,cx,cy,wid,hei):
    pygame.draw.rect(screen,color,pygame.Rect(cx-0.5*wid,cy-0.5*hei,wid,hei))

def drawText(screen,text,size,cx,cy,font='arial',color=(0,0,0)):
    font=pygame.font.SysFont(font,size)
    text=font.render(text,True,color)
    x,y=cx-text.get_width()/2,cy-text.get_height()/2
    screen.blit(text,(x,y))
    # learned from http://www.nerdparadise.com/programming/pygame/part5

def drawImage(screen,path,pos):
    screen.blit(getImage(d,path),pos)

def update(d): pass

def everySec(d):
    if d.flag != None:
        d.flagWait -= 1000;
        if d.flagWait == 0: d.flag = None; d.flagText = None
    Buttons.checkHover(d)
    if d.moveInVils:
        Villagers.moveIn(d)
        d.moveInVils = False; d.newHouse = None
    for vil in Villager.pop:
        if bool(vil.wait): # waiting
            vil.waited += 1000
            if vil.wait <= vil.waited:
                vil.wait = vil. waited = 0
        elif vil.idle and vil.state=='idle':
            vil.walkAround(d)

def everyThreeSec(d):
    Villagers.rearrangeHousing(d)
    Villagers.findIdle()
    for vil in Villager.pop:
        vil.hunger += 1.5
        Villagers.dead(d)
    Resources.update(d)
    for tree in Tree.placed:
        tree.time += 3000
        if tree.time >= 120000:
            tree.time %= 120000
            tree.age(d)
    for farm in Farm.placed:
        farm.findMaturity(d)

def everyThirtySec(d):
    Resources.newTrees(d)
    Villagers.newBabies(d)

def time(time,d):
    d.threeSec += pygame.time.get_ticks() - d.lastClick
    d.oneSec += pygame.time.get_ticks() - d.lastClick
    d.thirtySec += pygame.time.get_ticks() - d.lastClick
    if d.threeSec >= 3000:
        d.threeSec %= 3000
        everyThreeSec(d)
    if d.oneSec >= 1000:
        d.oneSec %= 1000
        everySec(d)
    if d.thirtySec >= 30000:
        d.thirtySec %= 30000
        everyThirtySec(d)
    d.lastClick = time.get_ticks()


def run():
    pygame.init()
    class Struct(object): pass
    d = Struct()
    init(d)
    screen = pygame.display.set_mode((d.width, d.height))#,pygame.FULLSCREEN
    clock = pygame.time.Clock()
    startMenuInit(d)
    gameInit(d)
    pygame.display.set_caption('Home Again')
    d.i = 0
    # pygame.mixer.music.load('Beethoven.mp3')
    # pygame.mixer.music.set_volume(0.2)
    # pygame.mixer.music.play(-1,0.0)
    while not d.done:
        if pygame.mouse.get_pressed()[0]:
            Buttons.checkTime(d)
            pygame.time.delay(100)
        if not d.pause:
            clock.tick(d.tick)
            time(pygame.time,d)
        for event in pygame.event.get():
            checkQuit(screen,d,event)
            if d.mode=='start':
                startMenuEvents(d)
            elif d.mode=='game' and not d.pause:
                gameEvents(event,d)
            elif d.mode=='help':
                helpEvents(event,d)
            elif d.mode=='story':
                helpEvents(event,d)
        if d.mode=='start': startMenuDraw(screen,d)
        elif d.mode=='game'and not d.pause:
            for vil in Villager.pop:
                if vil.moving:
                    vil.update(d)
            gameDraw(screen,d)
        elif d.mode == 'story': storyDraw(screen,d)
        elif d.mode == 'help' : helpDraw(screen,d)
        # d.v1.draw(screen,d)
        pygame.display.update()
        # pygame.draw.rect(screen, color, pygame.Rect(x, y, 60, 60))
        # drawimage(screen,'ring.png',(100,100))
        # pygame.display.flip()
run()
