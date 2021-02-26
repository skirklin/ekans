import asyncio
import curses
import random
from .drawable import Drawable
from .snake import Snake
from .apple import Apple


class Board(Drawable):
    """
    Represent the state of the game board.
    """

    def __init__(self, app, dims):
        self.app = app

        self.dims = dims
        self.border = 2
        self.apples = set()
        while len(self.apples) < 10:
            self.add_apple()

        self.snake = Snake.Make(x=dims[0] // 2, y=dims[1] // 2)

    def add_apple(self):
        rand_x = random.choice(range(self.dims[0]))
        rand_y = random.choice(range(self.dims[1]))
        char = self.app.stdscr.instr(rand_y, rand_x, 1).decode()
        if char == " ":
            self.apples.add(Apple(rand_x, rand_y))

    def draw(self, scr):
        for x in range(self.dims[0]):
            for y in range(self.dims[1]):
                scr.insstr(y, x, " ")
        for apple in self.apples:
            apple.draw(scr)
        self.snake.draw(scr)

    async def listen(self, scr):
        while True:
            key = scr.getkey()
            print(key)

    async def run(self):
        asyncio.create_task(self.snake.run())
        loop = asyncio.get_running_loop()
        loop.call_soon_threadsafe(self.listen, self.app.stdscr)
