from .drawable import Drawable

class Apple(Drawable):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, scr):
        scr.insstr(self.y, self.x, "#")