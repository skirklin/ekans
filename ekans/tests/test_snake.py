from ..snake import Snake
from ..window import VirtualWindow
from ..board import Board
from ..app import Application

def test_snake():
    vw = VirtualWindow((20, 20), [])
    app = Application(vw)
    b = Board(app, vw)
    b.snake.head.fwd_dir()
    b.snake.head.back_dir()