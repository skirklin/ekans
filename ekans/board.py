import random
import time
from .drawable import Drawable
from .snake import Snake
from .apple import Apple
from .barrier import Barrier


class Board(Drawable):
    """
    Represent the state of the game board.
    """

    def __init__(self, app, window):
        self.app = app
        self.window = window

        self.apples = set()
        self.add_apples()

        self.barriers = set()
        self.add_border()

        x_dim,y_dim = self.window.shape
        self.snake = Snake.Make(x=x_dim // 2, y=y_dim // 2, board=self)
        
    def add_apples(self):
        while len(self.apples) < 10:
            self.add_apple()

    def add_apple(self):
        rand_x = random.choice(range(self.window.shape[0]))
        rand_y = random.choice(range(self.window.shape[1]))
        elt = self.window.get_obj(rand_x, rand_y)
        if elt is None:
            self.apples.add(Apple(self, rand_x, rand_y))


    def add_border(self):
        for x in range(self.window.shape[0]):
            self.barriers.add(Barrier(self, x,  0))
            self.barriers.add(Barrier(self, x, -1))
        for y in range(self.window.shape[1] - 1):
            self.barriers.add(Barrier(self,  0, y))
            self.barriers.add(Barrier(self, -1, y))


    def draw(self):
        self.window.clear()
        for apple in self.apples:
            apple.draw()
        for barrier in self.barriers:
            barrier.draw()
        self.snake.draw()

    def install_handlers(self, app):
        self.snake.install_handlers(app)

    def tick(self):
        self.snake.tick()

    def game_over(self):
        self.app.stop(None)