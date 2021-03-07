import time
import random

from .base import HeadlessController
from ..segment import Segment
from ..barrier import Barrier


from ..directions import KEY_MAP


class AIController(HeadlessController):
    pass


class RandomAIContoller(AIController):
    def events(self, app):
        yield " "
        snake = app.board.snake

        def check(k):
            d = KEY_MAP[k]
            if d == snake.head.back_dir():
                return False
            p = snake.peek(d)
            hit = snake.window.get_obj(*p)
            if isinstance(hit, (Barrier, Segment)):
                return False
            return True

        while not app.board.game_is_over():
            options = [k for k in KEY_MAP.keys() if check(k)]
            app.debug_lines.append(repr(options))
            if options:
                next_dir = random.choice(options)
            else:
                # yield the same as last time, because it doesn't matter
                pass
            yield next_dir
