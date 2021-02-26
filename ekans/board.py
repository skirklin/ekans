import random
import numpy as np
import time
from .drawable import Drawable
from .snake import Snake
from .apple import Apple
from .barrier import Barrier


class Board(Drawable):
    """
    Represent the state of the game board.
    """

    def __init__(self, app, window, num_apples=0.01):
        self.app = app
        self.window = window
        x_dim,y_dim = self.window.shape
        self.snake = Snake.Make(x=x_dim // 2, y=y_dim // 2, board=self)

        if num_apples < 1:
            num_apples = x_dim*y_dim*num_apples
        self.num_apples = num_apples
        self.apples = set()
        self.add_apples()

        self.barriers = set()
        self.add_border()

        
    def add_apples(self):
        grid_size = self.window.shape[0]*self.window.shape[1]
        snake_size = len(self.snake)
        available_space = grid_size - snake_size
            
        while len(self.apples) < min(available_space, self.num_apples):
            self.add_apple()

    def add_apple(self):
        loc = random.choice(np.argwhere(self.window.objects == None))
        self.apples.add(Apple(self, *loc))


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
        self.add_apples()

    def game_over(self):
        self.app.stop(None)