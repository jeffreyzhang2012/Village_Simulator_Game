import math
def x(n):
    return n/1076*320

def y(n):
    return n/803*240

x1 = 468+18
x2 = 540+15
y1 = 648+18
y2 = 726
h = y2-y1
ratio = 1.6
orthoX = h*ratio
realx = x2-x1
angle = math.acos(realx/orthoX)
realtopix = 5/h
distance = ((1076/2)/math.tan(30.5*3.1415/180))*realtopix
print(distance/12)
print(distance/24)
print(math.tan(angle)*distance/24)
print(angle*180/3.1415)