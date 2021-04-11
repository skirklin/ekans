import mock
import random
import pytest

from ekans.pathing import Partition, field
from ekans.board import Board
from ekans.app import Application
from ekans.window import VirtualWindow
from ekans.player import ScriptedPlayer

def _diamond(app):
    b = app.board
    for i in range(3):
        b._add_barrier(5+i, 5-i)
        b._add_barrier(5+i, 5+i)
        b._add_barrier(7+i, 7-i)
        b._add_barrier(7+i, 3+i)

def _open_box(app):
    b = app.board  
    for i in range(4):
        b._add_barrier(3, i+3)
        b._add_barrier(6, i+3)
        b._add_barrier(i+3, 3)

def _box(app):
    b = app.board
    for i in range(4):
        b._add_barrier(3, i+3)
        b._add_barrier(6, i+3)
        b._add_barrier(i+3, 3)
        b._add_barrier(i+3, 6)

def _random(app):
    b = app.board
    for _ in range(10):
        b._add_barrier(
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
def snake(request):
    vw = VirtualWindow((20, 20))
    app = Application(vw, seed=1234)
    s = app.board.add_snake(ScriptedPlayer.Factory([]), app.board.CENTER)
    f = _plans[request.param]
    f(app)
    return s

def test_partition(request, snake):
    print(request)
    snake.board.draw()
    seg = Partition(snake, snake.board).compute()
    print()
    print(str(snake.board.window))
    print(seg.T)


def test_field(snake):
    snake.board.draw()
    p = field(snake.board)
    print((p*10000).astype(int))
    print(str(snake.board.window))
