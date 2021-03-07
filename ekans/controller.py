import abc
import time


class Controller(abc.ABC):
    @abc.abstractmethod
    def run(self, app):
        pass


class KeyboardController(Controller):
    def __init__(self, window):
        self.window = window

    def run(self, app):
        app.run_realtime()
        while not app._stop:
            try:
                event = self.window.stdscr.getkey()
                app.handle(event)
            except KeyboardInterrupt:
                app.stop()


class AIController(Controller):
    pass


class ScriptedController(Controller):
    def __init__(self, events):
        self.events = events

    def run(self, app):
        for event in self.events:
            app.handle(event)
