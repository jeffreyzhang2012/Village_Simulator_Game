class Maze(object):

    def fillDistances(maze,startR,startC,endR,endC):
        madeFill = None
        rows, cols = len(maze),len(maze[0])
        # print(rows,cols,'rc')
        # print(endR,endC,'endRC')
        maze[endR][endC] = '0'# use string to avoid confustion with True
        for row in range(rows):
            for col in range(cols):
                if not isinstance(maze[row][col],str): continue
                for (drow,dcol) in [(-1,0),(0,1),(1,0),(0,-1)]:
                    adjRow,adjCol = drow+row, dcol + col
                    if not (0<=adjRow<rows and 0<=adjCol<cols):continue
                    if maze[row+drow][col+dcol]==True:
                        maze[row+drow][col+dcol]=str(int(maze[row][col])+1)
                        madeFill = True
        if not madeFill: return 'dead' # some areas not reached
        return maze

    def makePath(maze,startR,startC,topR,topC):
        if not isinstance(maze[startR][startC],str): return None
        path = []
        rows, cols = len(maze), len(maze[0])
        pathLen = int(maze[startR][startC])
        row,col = startR, startC
        # path.append((row,col))
        while len(path) < pathLen: # include start and end, so +1
            curDistance = int(maze[row][col])
            for (drow,dcol) in [(-1,0),(0,1),(1,0),(0,-1)]:
                adjRow,adjCol = drow+row, dcol + col
                if not (0<=adjRow<rows and 0<=adjCol<cols):continue
                if maze[adjRow][adjCol]==None: continue
                if int(maze[row+drow][col+dcol])==curDistance - 1:
                    row,col = row+drow, col+dcol
                    path.append([row+topR,col+topC])
        return path

    def solveMaze(maze,topR,topC,startR,startC,endR,endC):
        startR -= topR; endR -= topR; startC -= topC; endC -= topC
        # print(topR,topC,'top')
        # print(startR,startC,'start')
        # print(endR,endC,'end')
        dead = None
        rows, cols = len(maze),len(maze[0])
        for row in range(rows):
            while True in maze[row]:
                temp = maze
                maze=Maze.fillDistances(maze,startR,startC,endR,endC)
                if maze == 'dead': # some places unreachable
                    dead = True
                    maze = temp
                    break
            if dead: break
        solution = Maze.makePath(maze,startR,startC,topR,topC)
        return solution