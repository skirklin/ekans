import threading
import numpy as np
import time

from .board import Board
from .events import TICK


# TODOS:
#  - handle pane resizing
#  - score keeping
#  - virtualized play for adding AI strategies


class Application:
    def __init__(
        self,
        window,
        max_shape=None,
        debug_console_height=3,
    ):
        self._stop = False
        self._handlers = {}
        self._tick_lock = threading.Lock()
        self._last_tick = 0
        self.max_shape = max_shape

        self.debug_console_height = debug_console_height
        self.debug_lines = []

        self.window = window  # total screen
        self.window.install_handlers(self)
        self.setup_board()

    def setup_board(self):
        shape = self.window.shape
        max_shape = self.max_shape
        if max_shape:
            shape = (
                min(self.max_shape[0], shape[0]),
                min(self.max_shape[1], shape[1]),
            )

        # top line as app status line
        # bottom line as game status line
        status_height = 1
        self.board = Board(
            self,
            self.window[
                0 : shape[0], self.debug_console_height : shape[1] - status_height
            ],
        )
        self.board.pause()

    def set_status(self, msg):
        console = msg.ljust(self.window.shape[0])
        self.window.addstr(0, -1, console, None)

    def add_handler(self, event, handler):
        try:
            handlers = self._handlers[event]
        except KeyError:
            handlers = self._handlers[event] = []

        if handler in handlers:
            self.debug_lines.append(f"Multiple copies of {handler} installed for {event}")
        handlers.append(handler)

    def remove_handler(self, event, handler):
        try:
            handlers = self._handlers[event]
        except KeyError:
            self.debug_lines.append(f"Cannot remove handler for unknown event {event}")
        else:
            try:
                handlers.remove(handler)
            except ValueError:
                self.debug_lines.append(
                    f"Cannot remove {handler} from {event}, it isn't registered"
                )

    def stop(self):
        self._stop = True

    def is_stopped(self):
        return self._stop

    def _record(self, event):
        self.debug_lines.append(f"EVENT: {event}")

    def handle(self, event, payload=None):
        for handler in self._handlers.get(event, []):
            try:
                handler(self, event, payload or {})
            except Exception:
                import traceback

                self.debug_lines += traceback.format_exc().split("\n")

    def draw(self):
        with self.window.lock:
            self.window.clear()
            self.board.draw()
            self._draw_status()
            self._draw_debug()

    def _draw_status(self):
        # Some board state is not rendered in the board, but the App may choose to present it
        width = self.board.window.shape[0]
        template = "{{status:<{stw}}}{{score:<{scw}}}".format(stw=width - 10, scw=10)
        statusline = template.format(
            status=self.board.status, score=f"score: {self.board.snake.score}"
        )
        self.window.addstr(0, -1, statusline, None)

    def _draw_debug(self):
        if self.debug_console_height:
            for i, line in enumerate(self.debug_lines[-self.debug_console_height :]):
                dl = line.ljust(self.window.shape[0])
                self.window.addstr(0, i, dl, None)

    def tick(self):
        self.handle(TICK)
        with self._tick_lock:
            self._last_tick = time.time()
            self.board.tick(self)
            self.draw()
