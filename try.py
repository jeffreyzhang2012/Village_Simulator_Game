import pygame

# class Struct():pass
# d = Struct()
# d.y = 6
# A = JK(4)
# print(A.calc(d))
class A(object):
    f = 9393
    def __init__(self,x,y):
        self.x = x

    def f(self):
        print(self.x)
        print(55)
        self.fuck = 8989

class B(A):
    def __init__(self,x,y):
        self.x = x*20
        self.k = x*3
    def print(self):
        print('fuck')

class C(A):
    def __init__(self,x,y):
        self.x = x
        self.z = z
    def _init_(self):
        self.x = self.x * 2
        self.hunger = 9
    def print(self):
        print('oh')

fuck = B(2,3)
fuck.__class__ = C
fuck._init_()
print(fuck.k)
fuck.print()
print(fuck.x)
print(fuck.hunger)
# # a = C(2,3)
# # a.f()
# a= B(2,3)
# def fuck(obj):
#     print (obj.f())
#     print(obj.fuck)

# fuck(a)
import os
path = os.listdir()
print(path)
for file in os.listdir('vil\\f'):
    file = 'vil\\f\\' + file
    # name = 'vil\\f\\L'+str(int(file.split(' ')[-1][:2])-71)
    if not '.png' in file:
        os.rename(file,file+'.png')