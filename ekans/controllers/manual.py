import time

from .base import HeadlessController


class ManualController(HeadlessController):
    def __init__(self, events, wait=0, block=False):
        self._events = events
        super().__init__(wait=wait, block=block)

    def events(self, app):
        yield from self._events
