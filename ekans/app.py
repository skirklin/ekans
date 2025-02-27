import threading
import numpy as np
import time
import random

from .board import Board
from .events import TICK
from . import levels


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
        seed=None,
        tick_rate=5,
        level="Bars()"
    ):
        self._stop = False
        self.board = None
        self._handlers = {}
        self._tick_lock = threading.Lock()
        self._tick_rate = tick_rate
        self._last_tick = 0
        self.max_shape = max_shape
        self.random = random.Random(seed)

        self.debug_console_height = debug_console_height
        self.debug_lines = []

        self.window = window  # total screen
        self.window.install_handlers(self)
        self.set_level(level)
        self.setup_board()

    def set_level(self, level):
        level_classes = {
            k: o
            for k, o in levels.__dict__.items()
            if isinstance(o, type) and issubclass(o, levels.Level)
        }
        try:
            self.level = eval(level, level_classes)
            self.debug_lines.append(f"Set level: {level}")
        except Exception:
            options = ", ".join(level_classes)
            self.level = levels.EmptyLevel()
            self.debug_lines.append(f"Failed to interpret level {level}, make sure it is an option: {options}")

    def setup_board(self):
        if self.board is not None:
            self.board.remove_handlers()

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
        self.board.install_handlers()
        self.level.apply(self.board)
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


    def run_realtime(self):
        t = threading.Thread(target=self._run_realtime)
        t.setDaemon(True)
        t.start()

    def _run_realtime(self):
        interval = 1 / self._tick_rate
        while not self.is_stopped():
            time.sleep(1 / self.window._refresh_rate)
            if time.time() - self._last_tick > interval:
                self.tick()
        
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
            self.debug_lines.append(str(self.window.attrs.sum()))

            self.window.clear()
            self.board.draw()
            self._draw_status()
            self._draw_debug()

    def _draw_status(self):
        # Some board state is not rendered in the board, but the App may choose to present it
        width = self.board.window.shape[0]
        template = "{{status:<{stw}}}{{score:<{scw}}}".format(stw=width - 10, scw=10)
        if len(self.board.snakes) > 1: 
            scores = " | ".join(["{i}={s.score}" for i, s in enumerate(self.board.snakes)])
        elif len(self.board.snakes) == 1:
            s = self.board.snakes[0]
            scores = str(s.score)
        else:
            scores = "NA"
        statusline = template.format(
            status=self.board.status, score=scores,
        )
        self.window.addstr(0, -1, statusline, None)

    def _draw_debug(self):
        if self.debug_console_height:
            for i, line in enumerate(self.debug_lines[-self.debug_console_height :]):
                dl = str(line).ljust(self.window.shape[0])
                self.window.addstr(0, i, dl, None)

    def tick(self):
        self.handle(TICK)
        with self._tick_lock:
            self._last_tick = time.time()
            self.board.tick()
            self.draw()