from ekans.snake import Snake
from ekans.window import VirtualWindow
from ekans.board import Board
from ekans.app import Application


def test_snake():
    vw = VirtualWindow((20, 20))
    app = Application(vw)
    app.board.snake.head.d
    app.board.snake.head.back