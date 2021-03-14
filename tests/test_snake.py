from ekans.snake import Snake
from ekans.window import VirtualWindow
from ekans.board import Board
from ekans.app import Application


def test_snake():
    vw = VirtualWindow((20, 20))
    app = Application(vw)
    app.board.snake.head.fwd_dir()
    app.board.snake.head.back_dir()