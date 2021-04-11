from ekans.snake import Snake
from ekans.window import VirtualWindow
from ekans.board import Board
from ekans.app import Application
from ekans.player import ScriptedPlayer

def test_snake():
    player_factory = ScriptedPlayer.Factory([])

    vw = VirtualWindow((20, 20))
    app = Application(vw)
    s = app.board.add_snake(player_factory, app.board.CENTER)
    s.head.d
    s.head.back