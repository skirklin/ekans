import time
from ekans.window import VirtualWindow, CursesWindow


def test_window_functionality():
    w = VirtualWindow((20, 15))
    assert (10, 10) in w
    assert (19, 14) in w
    assert (0, 6) in w
    assert (20, 15) not in w
    assert (30, 10) not in w
    assert (-6, 10) not in w
    print(list(map(lambda x: x.shape, w.coords)))
