from .app import Application
from .window import CursesWindow

with CursesWindow() as window:
    app = Application(window)
    app.start()