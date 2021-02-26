from .drawable import Drawable

class Apple(Drawable):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, window):
        window.insstr(self.x, self.y, "#")