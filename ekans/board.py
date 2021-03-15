import traceback
import numpy as np
import time
import enum
from .drawable import Drawable
from .snake import Snake
from .apple import Apple
from .barrier import Barrier
from .events import ADD_APPLE, REMOVE_APPLE


class State(enum.Enum):
    INIT = 0
    RUNNING = 1
    PAUSED = 2
    GAME_OVER = 3


class Board(Drawable):
    """
    Represent the state of the game board.
    """

    def __init__(self, app, window, level="Bars()", num_apples=0.01):
        self.app = app
        self._state = State.INIT
        self.window = window
        self.snake = None
        x_dim, y_dim = self.window.shape

        self.barriers = set()
        self.apples = set()
        self.add_border()

        self.draw()
        self.snake = Snake.Make(x=x_dim // 2, y=y_dim // 2, board=self)
        self.install_handlers()

        if num_apples < 1:
            num_apples = x_dim * y_dim * num_apples

        self.num_apples = num_apples
        self.add_apples()
        self.status = ""


    def add_apples(self):
        grid_size = self.window.shape[0] * self.window.shape[1]
        snake_size = len(self.snake)
        self.snake.draw()
        available_space = grid_size - snake_size

        while len(self.apples) < min(available_space, self.num_apples):
            self.add_apple()

    def add_apple(self):
        loc = self.app.random.choice(np.argwhere(self.window.objects == None))
        assert self.window.get_obj(*loc) is None, self.window.get_obj(*loc)
        a = Apple(self, *loc)
        self.app.handle(ADD_APPLE, {"apple": a})

    def _remove_apple(self, app, event, payload):
        self.apples.remove(payload["apple"])

    def _add_apple(self, app, event, payload):
        self.apples.add(payload["apple"])

    def add_barrier(self, x, y):
        self.barriers.add(Barrier(self, x, y))

    def add_border(self):
        for x in range(self.window.shape[0]):
            self.add_barrier(x, 0)
            self.add_barrier(x, self.window.shape[1] - 1)
        for y in range(self.window.shape[1] - 1):
            self.add_barrier(0, y)
            self.add_barrier(self.window.shape[0] - 1, y)

    def draw(self):
        self.window.clear()
        for apple in self.apples:
            apple.draw()
        for barrier in self.barriers:
            barrier.draw()
        if self.snake is not None:
            self.snake.draw()

    def install_handlers(self):
        self.snake.install_handlers(self.app)
        self.app.add_handler(" ", self.toggle_pause)
        self.app.add_handler(ADD_APPLE, self._add_apple)
        self.app.add_handler(REMOVE_APPLE, self._remove_apple)

    def remove_handlers(self, app):
        self.snake.remove_handlers(app)
        self.app.remove_handler(" ", self.toggle_pause)
        self.app.remove_handler(ADD_APPLE, self._add_apple)
        self.app.remove_handler(REMOVE_APPLE, self._remove_apple)

    def game_is_over(self):
        return self._state is State.GAME_OVER

    def game_is_running(self):
        return self._state is State.RUNNING

    def game_is_paused(self):
        return self._state is State.PAUSED

    def toggle_pause(self, app, event, payload):
        if self._state is State.RUNNING:
            self.pause()
        elif self._state in (State.PAUSED, State.INIT):
            self.resume()
        else:
            self.remove_handlers(app)
            app.setup_board()

    def pause(self):
        self._state = State.PAUSED
        self.status = "Paused: press <space> to resume"

    def resume(self):
        if not self.game_is_paused():
            raise RuntimeError(
                f"Cannot resume from state other than paused, got {self._state}"
            )
        self._state = State.RUNNING
        self.status = ""

    def tick(self, app):
        if self.game_is_running():
            self.snake.tick(app)
            self.add_apples()

    def game_over(self):
        self._state = State.GAME_OVER
        self.status = "Game over, press <space> to start over"
