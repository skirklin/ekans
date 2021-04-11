import traceback
import numpy as np
import time
import enum
from .drawable import Drawable
from .snake import Snake
from .apple import Apple
from .barrier import Barrier
from .events import ADD_APPLE, REMOVE_APPLE, ADD_BARRIER, REMOVE_BARRIER, ADD_SNAKE, REMOVE_SNAKE


class State(enum.Enum):
    INIT = 0
    RUNNING = 1
    PAUSED = 2
    GAME_OVER = 3


class Board(Drawable):
    """
    Represent the state of the game board.
    """

    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"

    def __init__(self, app, window, num_apples=0.01):
        self.app = app
        self._state = State.INIT
        self.window = window
        self.snakes = []

        self.barriers = set()
        self.apples = set()
        self.add_border()

        x_dim, y_dim = self.window.shape
        if num_apples < 1:
            num_apples = x_dim * y_dim * num_apples

        self.num_apples = num_apples
        self.draw()
        self.status = ""

    def clear(self):
        for s in list(self.snakes):
            self.app.handle(REMOVE_SNAKE, {"snake": s})
        for b in list(self.barriers):
            self.app.handle(REMOVE_BARRIER, {"barrier": b})
        for a in list(self.apples):
            self.app.handle(REMOVE_APPLE, {"apple": a})

    def set_level(self, level):
        self.clear()

    def add_snake(self, player, position, **kwargs):
        assert position in (self.CENTER, self.LEFT, self.RIGHT), position
        x_dim, y_dim = self.window.shape
        y_pos = y_dim // 2
        if position == self.CENTER:
            x_pos = x_dim // 2
        elif position == self.LEFT:
            x_pos = x_dim // 3
        elif position == self.RIGHT:
            x_pos = (x_dim * 2) // 3

        s = Snake.Make(self, player, x_pos, y_pos, **kwargs)
        s.install_handlers()
        s.draw()
        self.snakes.append(s)
        return s

    def ensure_apples(self):
        available_space = (self.window.objects == None).sum()

        while len(self.apples) < min(available_space, self.num_apples):
            self.add_apple()

    def add_apple(self):
        loc = self.app.random.choice(np.argwhere(self.window.objects == None))
        assert self.window.get_obj(*loc) is None, self.window.get_obj(*loc)
        a = Apple(self, *loc)
        self.app.handle(ADD_APPLE, {"apple": a})

    def _handle_remove_apple(self, app, event, payload):
        self.apples.remove(payload["apple"])

    def _handle_add_apple(self, app, event, payload):
        a = payload["apple"]
        assert self.window.get_obj(a.x, a.y) is None, self.window.get_obj(a.x, a.y)
        self.apples.add(a)
        a.draw()

    def _add_barrier(self, x, y):
        b = Barrier(self, x, y)
        curr = self.window.get_obj(b.x, b.y)
        if isinstance(curr, Barrier):
            return
        assert curr is None, self.window.get_obj(b.x, b.y)
        self.barriers.add(b)
        b.draw()

    def _remove_barrier(self, barrier):
        self.barriers.remove(barrier)

    def add_border(self):
        for x in range(self.window.shape[0]):
            self._add_barrier(x, 0)
            self._add_barrier(x, self.window.shape[1] - 1)
        for y in range(self.window.shape[1] - 1):
            self._add_barrier(0, y)
            self._add_barrier(self.window.shape[0] - 1, y)

    def draw(self):
        self.window.clear()
        for apple in self.apples:
            apple.draw()
        for barrier in self.barriers:
            barrier.draw()
        for snake in self.snakes:
            snake.draw()

    def events(self):
        return {
            " ": self.toggle_pause,
            ADD_APPLE: self._handle_add_apple,
            REMOVE_APPLE: self._handle_remove_apple,
        }

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

    def tick(self):
        if self.game_is_running():
            for snake in self.snakes:
                snake.tick()
            self.ensure_apples()

    def game_over(self):
        self._state = State.GAME_OVER
        self.status = "Game over, press <space> to start over"

    def next_color(self):
        return 34