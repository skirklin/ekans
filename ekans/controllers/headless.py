import abc
import os

from .base import Controller

class HeadlessController(Controller):
    def __init__(self, window, wait=0, block=False):
        self.wait = wait
        self.block = block
        self.window = window
        if audit_log := os.environ.get("EKANS_AUDIT_LOG"):
            self._audit_events = []
            self._audit_log = open(audit_log, 'w')
        else:
            self._audit_events = []
            self._audit_log = None

    def record(self, **kwargs):
        self._audit_events.append(kwargs)

    def run(self, app):
        app.handle(" ")
        while not app.board.game_is_over():
            app.tick()
            self.window.render()