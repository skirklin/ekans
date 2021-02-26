import time
from ..window import VirtualWindow, CursesWindow

def test_curses_window():
    with CursesWindow() as window:
        window.insstr(5, 5, "$", None)
        window.render()

def test_window_functionality():
    w = VirtualWindow((20, 20), [])
    assert (10, 10) in w
    assert (19, 19) in w
    assert (0, 6) in w
    assert (20, 20) not in w
    assert (30, 10) not in w
    assert (-6, 10) not in w