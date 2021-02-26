import asyncio
import random
import time
from .drawable import Drawable
from .snake import Snake
from .apple import Apple

"""
TODO: 
  put screen state into an array here, and move all rendering and curses integration here

"""


class Board(Drawable):
    """
    Represent the state of the game board.
    """

    def __init__(self, window):
        self.window = window

        

        self.apples = set()
        while len(self.apples) < 10:
            self.add_apple()

        x_dim,y_dim = self.window.shape
        self.snake = Snake.Make(x=x_dim // 2, y=y_dim // 2, window=self.window)

    def add_apple(self):
        rand_x = random.choice(range(self.window.shape[0]))
        rand_y = random.choice(range(self.window.shape[1]))
        char = self.window.instr(rand_x, rand_y)
        if char == " ":
            self.apples.add(Apple(rand_x, rand_y))

    def draw(self, window):
        for x in range(self.window.shape[0]):
            for y in range(self.window.shape[1]):
                window.insstr(x, y, " ")
        for apple in self.apples:
            apple.draw(window)
        self.snake.draw(window)

    async def run(self):
        asyncio.create_task(self.snake.run())
