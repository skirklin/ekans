import os
from .app import Application
from .window import CursesWindow, VirtualWindow


with CursesWindow() if not os.environ.get("EKANS_DEBUG") else VirtualWindow((20, 20), []) as window:
    app = Application(window)
    app.run()