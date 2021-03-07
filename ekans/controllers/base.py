import abc
import time


class Controller(abc.ABC):
    @abc.abstractmethod
    def run(self, app):
        pass


class HeadlessController(Controller):
    def __init__(self, wait=0, block=False):
        self.wait = wait
        self.block = block

    @abc.abstractmethod
    def events(self, app):
        pass

    def run(self, app):
        for event in self.events(app):
            app.handle(event)
            app.tick()
            if self.wait:
                time.sleep(self.wait)
            app.draw()
        if self.block:
            while True:
                time.sleep(1)
