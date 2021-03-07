import curses
import threading
import numpy as np
import time
import io

from .controller import KeyboardController


class Window:
    def __init__(self, pixels):
        self.set_pixels(pixels)
        self.clear()
        self.lock = threading.RLock()

    def set_pixels(self, pixels):
        self.pixels = pixels
        self.objects = np.empty_like(pixels, dtype=object)

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
        return cls(np.empty(shape, dtype=str))

    def __contains__(self, coord):
        for i, d in enumerate(coord):
            if d < 0 or d >= self.shape[i]:
                return False
        return True

    def __getitem__(self, *args):
        return Window(self.pixels.__getitem__(*args))

    def insstr(self, x, y, char, obj):
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

    def instr(self, x, y):
        return self.pixels[x, y]

    def addstr(self, x, y, chars, obj):
        for i, c in enumerate(chars):
            if x + i >= self.pixels.shape[0]:
                break
            self.pixels[x + i, y] = c
            self.objects[x + i, y] = obj

    def clear(self):
        self.pixels[:] = " "
        self.objects[:] = None

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
    def __init__(self, shape):
        pixels = np.empty(shape, dtype=str)
        super().__init__(pixels)

    def render(self):
        # VirtualWindows don't really get drawn.
        return


class CursesWindow(Window):
    def __init__(self, refresh_rate=30):
        # start with an "empty" window, which will be filled in within the running context
        pixels = np.empty((0, 0), dtype=str)
        super().__init__(pixels)
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
        self.logfile = open("log", "a+")
        self.stdscr = curses.initscr()
        shape = (curses.COLS, curses.LINES)  # pylint: disable=no-member
        self.set_pixels(np.empty(shape=shape, dtype=str))
        self.clear()
        self.stdscr.keypad(True)

        curses.curs_set(False)
        curses.noecho()
        curses.cbreak()
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
        self.logfile.close()

    def install_handlers(self, app):
        super().install_handlers(app)
        app.add_handler("\x1b", app.stop)  # esc

    def controller(self):
        return KeyboardController(self)

    def render(self):
        with self.lock:
            for x in range(self.pixels.shape[0]):
                for y in range(self.pixels.shape[1]):
                    self.stdscr.insstr(y, x, self.pixels[x, y])
            self.stdscr.refresh()
