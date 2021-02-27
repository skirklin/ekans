from .drawable import Drawable

class Apple(Drawable):
    def __init__(self, board, x, y):
        self.x = x
        self.y = y
        self.board = board

    def draw(self):
        self.window.insstr(self.x, self.y, "@" if self.board._running else "X", self)

    @property
    def window(self):
        return self.board.window
        