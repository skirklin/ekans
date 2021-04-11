import curses
import threading
import numpy as np
import time
import io

from .events import TICK
from .controllers import InteractiveController, HeadlessController
from .player import HumanPlayer

class Window:
    def __init__(self, pixels, attrs, objects):
        self.lock = threading.Lock()
        self.set_pixels(pixels, attrs, objects)
        self.clear()

    def set_pixels(self, pixels, attrs, objects):
        self.pixels = pixels
        self.attrs = attrs
        self.objects = objects
        self.coords = np.meshgrid(
            range(self.pixels.shape[0]),
            range(self.pixels.shape[1]),
            indexing="ij",
        )

    def get_obj(self, x, y):
        """
        Return the object underlying the visible pixel at position (x, y)
        """
        return self.objects[x, y]

    @property
    def shape(self):
        return self.pixels.shape

    @classmethod
    def Create(cls, shape):
        return cls(np.empty(shape, dtype=str), np.empty(shape, dtype=int), np.empty(shape, dtype=object))

    def __contains__(self, coord):
        for i, d in enumerate(coord):
            if d < 0 or d >= self.shape[i]:
                return False
        return True

    def __getitem__(self, *args):
        return Window(self.pixels.__getitem__(*args), self.attrs.__getitem__(*args), self.objects.__getitem__(*args))

    def insstr(self, x, y, char, obj, attr=0):
        if x >= self.shape[0]:
            raise IndexError(
                f"index {x} is out of bounds for x-axis with size {self.shape[0]}"
            )
        if y >= self.shape[0]:
            raise IndexError(
                f"index {y} is out of bounds for x-axis with size {self.shape[1]}"
            )
        self.pixels[x, y] = char
        self.objects[x, y] = obj
        self.attrs[x, y] = attr

    def instr(self, x, y):
        return self.pixels[x, y]

    def addstr(self, x, y, chars, obj, attr=0):
        for i, c in enumerate(chars):
            if x + i >= self.pixels.shape[0]:
                break
            self.pixels[x + i, y] = c
            self.attrs[x + i, y] = attr
            self.objects[x + i, y] = obj

    def clear(self):
        self.pixels[:] = " "
        self.objects[:] = None
        self.attrs[:] = 0

    def render(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, *execDetails):
        return

    def install_handlers(self, app):
        pass

    def __str__(self):
        with self.lock:
            buf = io.StringIO()
            for y in range(self.pixels.shape[1]):
                for x in range(self.pixels.shape[0]):
                    buf.write(self.pixels[x, y])
                buf.write("\n")
        return buf.getvalue()


class VirtualWindow(Window):
    def __init__(self, shape, refresh_rate=30):
        pixels = np.empty(shape, dtype=str)
        attrs = np.empty(shape, dtype=int)
        objects = np.empty(shape, dtype=object)
        self._refresh_rate = refresh_rate
        super().__init__(pixels, attrs, objects)

    def render(self):
        print(str(self))

    def _log(self, app, event, payload):
        import sys
        sys.stdout.write(f"\rturn: {app.board.snake.turn} score: {app.board.snake.score}")

    def install_handlers(self, app):
        super().install_handlers(app)
        app.add_handler(TICK, self._log)

    def controller(self):
        return HeadlessController(self)

class CursesWindow(Window):
    def __init__(self, refresh_rate=30):
        # start with an "empty" window, which will be filled in within the running context
        pixels = np.empty((0, 0), dtype=str)
        attrs = np.empty((0, 0), dtype=int)
        objects = np.empty((0, 0), dtype=object)

        super().__init__(pixels, attrs, objects)
        self._stop = False
        self._refresh_rate = refresh_rate

    def _render_loop(self):
        while not self._stop:
            try:
                self.render()
                time.sleep(1 / self._refresh_rate)
            except KeyboardInterrupt:
                self._stop

    def __enter__(self):
        self.stdscr = curses.initscr()
        shape = (curses.COLS, curses.LINES)  # pylint: disable=no-member
        self.set_pixels(np.empty(shape, dtype=str), np.empty(shape, dtype=int), np.empty(shape, dtype=object))
        self.clear()
        self.stdscr.keypad(True)

        curses.curs_set(False)
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i, i, -1)

        # curses.set_escdelay(0), need 3.9

        self.render_thread = threading.Thread(target=self._render_loop)
        self.render_thread.start()

        return self

    def __exit__(self, *execDetails):
        self._stop = True
        self.render_thread.join()

        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def install_handlers(self, app):
        super().install_handlers(app)
        app.add_handler("\x1b", lambda app, event: app.stop())  # esc

    def controller(self):
        return InteractiveController(self)

    def render(self):
        with self.lock:
            for x in range(self.pixels.shape[0]):
                for y in range(self.pixels.shape[1]):
                    attr = self.attrs[x, y]
                    pixel = self.pixels[x, y]
                    self.stdscr.insstr(y, x, pixel, attr)
            self.stdscr.refresh()

    def human_player(self):
        return HumanPlayer.Factory(self)