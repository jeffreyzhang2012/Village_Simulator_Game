class JK(object):
    def __init__(self,x):
        self.x = x

    def fuck(self,d):
        return d.y * 3

    def calc(self,d):
        return JK.fuck(self,d) * self.x