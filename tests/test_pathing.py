import mock
import random
import pytest

from ekans.pathing import Partition, field
from ekans.board import Board
from ekans.app import Application
from ekans.window import VirtualWindow

def _diamond(app):
    b = app.board
    for i in range(3):
        b.add_barrier(5+i, 5-i)
        b.add_barrier(5+i, 5+i)
        b.add_barrier(7+i, 7-i)
        b.add_barrier(7+i, 3+i)

def _open_box(app):
    b = app.board  
    for i in range(4):
        b.add_barrier(3, i+3)
        b.add_barrier(6, i+3)
        b.add_barrier(i+3, 3)

def _box(app):
    b = app.board
    for i in range(4):
        b.add_barrier(3, i+3)
        b.add_barrier(6, i+3)
        b.add_barrier(i+3, 3)
        b.add_barrier(i+3, 6)

def _random(app):
    b = app.board
    for _ in range(10):
        b.add_barrier(
            app.random.choice(range(b.window.shape[0])),
            app.random.choice(range(b.window.shape[1])),
        )


_plans = {
    "box": _box,
    "open_box": _open_box,
    "diamond": _diamond,
    "random": _random,
}

@pytest.fixture(
    params=_plans.keys(),
)
def board(request):
    vw = VirtualWindow((20, 20))
    app = Application(vw, seed=1234)
    f = _plans[request.param]
    f(app)
    return app.board


def test_partition(request, board):
    print(request)
    board.draw()
    seg = Partition(board).compute()
    print()
    print(str(board.window))
    print(seg.T)


def test_field(board):
    board.draw()
    p = field(board)
    print((p*10000).astype(int))
    print(str(board.window))
