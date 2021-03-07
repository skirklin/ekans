import time

from .base import HeadlessController

class ManualController(HeadlessController):
    def __init__(self, events, wait=0):
        self._events = events
        self.wait = wait

    def events(self, app):
        yield from self._events