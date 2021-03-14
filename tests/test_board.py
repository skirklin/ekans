from ekans.snake import Snake
from ekans.window import VirtualWindow
from ekans.board import Board
from ekans.app import Application
from ekans.controllers.manual import ManualController


def test_self_collision():
    controller = ManualController([" ", "KEY_LEFT", "KEY_DOWN", "KEY_RIGHT"])
    vw = VirtualWindow((20, 20))  # this should direct a snake back into itself
    app = Application(vw, debug_console_height=0)
    controller.run(app)
    print()
    print(str(app.board.window))
    assert app.board.game_is_over()
