import os
from .app import Application
from .window import CursesWindow, VirtualWindow
from .controllers.manual import ManualController
from .controllers.ai import RandomAIContoller


with CursesWindow() as window:
    app = Application(window, max_shape=(100, 100))
    # controller = window.controller(tick_rate=5)
    # controller = ManualController([' ', 'KEY_LEFT', 'KEY_DOWN', 'KEY_RIGHT'], 0.5)
    controller = RandomAIContoller(0.01, block=True)
    controller.run(app)
