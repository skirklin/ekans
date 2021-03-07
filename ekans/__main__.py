import os
from .app import Application
from .window import CursesWindow, VirtualWindow
from .controller import KeyboardController


with CursesWindow() as window:
    app = Application(window, max_shape=(100, 100))
    controller = window.controller()
    controller.run(app)
