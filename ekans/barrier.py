from .drawable import Drawable


class Barrier(Drawable):
    def __init__(self, board, x, y):
        self.board = board
        self.window = board.window
        self.x = x
        self.y = y

    def draw(self):
        self.window.insstr(self.x, self.y, "#", self)
