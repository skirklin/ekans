import curses
import threading
import numpy as np


class Window:
    def __init__(self, pixels):
        self.set_pixels(pixels)
        self.clear()
        self.lock = threading.RLock()
    
    def set_pixels(self, pixels):
        self.pixels = pixels
        self.objects = np.empty_like(pixels, dtype=object)

    def get_obj(self, x, y):
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
            if x+i >= self.pixels.shape[0]:
                break
            self.pixels[x+i, y] = c
            self.objects[x+i, y] = obj

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


class VirtualWindow(Window):
    def __init__(self, shape, events):
        self.set_pixels(np.empty(shape, dtype=str))
        self._events = events  # an event generator
        self.clear()

    def events(self):
        yield from self._events

    def render(self):
        # VirtualWindows don't really get drawn.
        return


class CursesWindow(Window):
    def __init__(self):
        # start with an "empty" window, which will be filled in within the running context
        pixels = np.empty((0, 0), dtype=str)
        super().__init__(pixels)

    def __enter__(self):
        self.logfile = open("log", "a+")
        self.stdscr = curses.initscr()
        self.set_pixels(
            np.empty(
                shape=(curses.COLS, curses.LINES), dtype=str  # pylint: disable=no-member
            )
        )
        self.clear()
        self.stdscr.keypad(True)

        curses.curs_set(False)
        # curses.noecho()
        curses.cbreak()
        # curses.set_escdelay(0), need 3.9
        return self

    def __exit__(self, *execDetails):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        self.logfile.close()

    def install_handlers(self, app):
        super().install_handlers(app)
        app.add_handler('\x1b', app.stop)


    def events(self):
        while True:
            key = self.stdscr.getkey()
            with self.lock:
                if not isinstance(key, str):
                    raise Exception(f"What is {repr(key)}")
                console = repr(key).ljust(self.shape[0])
                self.addstr(0, -1, console, None)
                self.render()
            yield key

    def render(self):
        with self.lock:
            for x in range(self.pixels.shape[0]):
                for y in range(self.pixels.shape[1]):
                    self.stdscr.insstr(y, x, self.pixels[x, y])
            self.stdscr.refresh()