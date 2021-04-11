import time

from .base import Player
from ..directions import KEY_MAP


class ScriptedPlayer(Player):
    def __init__(self, snake, events):
        self.snake = snake
        self._events = events
        self.idx = 0

    def get_direction(self):
        try:
            d = KEY_MAP[self._events[self.idx]]
            self.idx += 1
        except IndexError:
            d = self.snake.direction
        return d

    @classmethod
    def Factory(cls, events):
        return lambda snake: cls(snake, events)