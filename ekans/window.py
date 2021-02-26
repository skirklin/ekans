import curses
import numpy as np


class Window:
    def __init__(self, pixels):
        self.pixels = pixels
        self.clear()

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

    def create_subwindow(self, anchor, shape):
        return Window(self.pixels[anchor[0] : shape[0], anchor[1] : shape[1]])

    def insstr(self, x, y, char):
        if x >= self.shape[0]:
            raise IndexError(
                f"index {x} is out of bounds for x-axis with size {self.shape[0]}"
            )
        if y >= self.shape[0]:
            raise IndexError(
                f"index {y} is out of bounds for x-axis with size {self.shape[1]}"
            )
        self.pixels[x, y] = char

    def instr(self, x, y):
        return self.pixels[x, y]

    def clear(self):
        self.pixels[:] = " "

    def render(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, *execDetails):
        return


class VirtualWindow(Window):
    def __init__(self, shape, events):
        self.pixels = np.empty(shape, dtype=str)
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
        self.pixels = np.empty(
            shape=(curses.COLS, curses.LINES), dtype=str  # pylint: disable=no-member
        )
        self.pixels[:] = " "
        self.stdscr.keypad(True)

        curses.curs_set(False)
        curses.noecho()
        curses.cbreak()
        return self

    def __exit__(self, *execDetails):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        self.logfile.close()

    def events(self):
        while True:
            key = self.stdscr.getstr()
            yield key

    def render(self):
        for x in range(self.pixels.shape[0]):
            for y in range(self.pixels.shape[1]):
                self.stdscr.insstr(y, x, self.pixels[x, y])
        self.stdscr.refresh()