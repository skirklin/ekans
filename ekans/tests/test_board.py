from ..snake import Snake
from ..window import VirtualWindow
from ..board import Board
from ..app import Application
from ..controller import ScriptedController


def test_self_collision():
    controller = ScriptedController([" ", "KEY_LEFT", "KEY_DOWN", "KEY_RIGHT"])
    vw = VirtualWindow((20, 20))  # this should direct a snake back into itself
    app = Application(vw, debug_console_height=0)
    controller.run(app)
    print()
    print(str(app.board.window))
    assert app.board.game_is_over()
