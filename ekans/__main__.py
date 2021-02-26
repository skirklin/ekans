import os
from .app import Application
from .window import CursesWindow, VirtualWindow


with CursesWindow() as window:
    app = Application(window) # , max_shape=(100, 100))
    app.run()