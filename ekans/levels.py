import abc


class Level:
    @abc.abstractmethod
    def apply(self, board):
        pass


class EmptyLevel(Level):
    def apply(self, board):
        return


class Bars(Level):
    def __init__(self, n=2, height=0.67):
        self.height = height
        self.n = n

    def apply(self, board):
        width, height = board.window.shape
        x = width // (self.n + 1)
        bar_height = int(height * self.height)
        margin = (height - bar_height) // 2

        for i in range(margin, height - margin):
            board.add_barrier(x, i)
            board.add_barrier(width - x, i)


class Random(Level):
    def __init__(self, n=0.1):
        self.n = n

    def apply(self, board):
        import numpy as np

        n = self.n
        if n < 1:
            width, height = board.window.shape
            n = int(self.n * (width - 2) * (height - 2))

        for _ in range(n):
            loc = board.app.random.choice(np.argwhere(board.window.objects == None))
            board.add_barrier(*loc)