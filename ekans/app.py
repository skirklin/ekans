import curses
import time
import asyncio

from .board import Board


class Application:
    def __init__(self, refresh_rate=30):
        self.stdscr = None
        self.stop = False
        self.refresh_rate = refresh_rate

    def start(self):
        if self.stdscr is None:
            raise RuntimeError("Must run application within application context")
        self.board = Board(
            self, dims=(curses.COLS, curses.LINES)  # pylint: disable=no-member
        )
        asyncio.run(self.run())

    async def run(self):
        asyncio.create_task(self.board.run())
        ticks = 60
        while ticks:
            self.draw(self.stdscr)
            await asyncio.sleep(1 / self.refresh_rate)
            ticks -= 1

    def draw(self, scr):
        curses.echo()
        self.board.draw(scr)
        scr.refresh()

    def __enter__(self):
        self.logfile = open("log", 'a+')
        self.stdscr = curses.initscr()
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