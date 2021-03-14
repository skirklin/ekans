import time
import random
import numpy as np
import json 

from .base import HeadlessController
from .. import vision
from ..barrier import Barrier
from ..segment import Segment
from ..directions import KEY_MAP
from ..events import ADD_APPLE, REMOVE_APPLE


class AIController(HeadlessController):
    pass


class RandomAIController(AIController):
    def events(self, app):
        yield " "
        while not app.board.game_is_over():
            options = list(KEY_MAP.keys())
            next_dir = random.choice(options)
            yield next_dir


class HungryAIController(AIController):
    def events(self, app):
        snake = app.board.snake
        window = snake.window
        field = vision.field(app.board)

        def _update_gradient_add(app, event, payload):
            vision.update_apple_field(window, payload["apple"], field, 1)

        def _update_gradient_remove(app, event, payload):
            vision.update_apple_field(window, payload["apple"], field, -1)

        try:
            app.add_handler(ADD_APPLE, _update_gradient_add)
            app.add_handler(REMOVE_APPLE, _update_gradient_remove)
            yield from self._events(app, field)
        finally:
            app.remove_handler(ADD_APPLE, _update_gradient_add)
            app.remove_handler(REMOVE_APPLE, _update_gradient_remove)

    
    def _events(self, app, field):
        snake = app.board.snake
        seg = None
        yield " "
        while not app.board.game_is_over():
            coord = snake.head.coord
            grad_x, grad_y = np.gradient(field)
            seg = vision.partition(app.board, seg)

            def tgt_func(k):
                d = KEY_MAP[k]
                g = [
                    grad_x[coord],
                    grad_y[coord],
                ]
                pi, pj = snake.peek(d)
                size = 0 if seg[pi, pj] == 0 else (seg == seg[pi, pj]).sum()
                return (-int(size), -np.dot(g, [d.dx, d.dy]))

            scores = {k: tgt_func(k) for k in KEY_MAP}

            if self._audit_log:
                self.record(
                    options=scores,
                    window=str(snake.window),
                    segmentation=seg.tolist(),
                )
            next_dir = min(scores, key=lambda x: scores[x])
            yield next_dir


class NaiveAIController(AIController):
    def events(self, app):
        yield " "
        snake = app.board.snake

        seg = None
        while not app.board.game_is_over():
            seg = vision.partition(app.board, seg)

            options = []
            for k, d in KEY_MAP.items():
                pi, pj = snake.peek(d)
                if seg[pi, pj] == 0:
                    # invalid location
                    continue
                size = (seg == seg[pi, pj]).sum()
                if size < len(snake) * 2:
                    continue
                options.append(k)

            # app.debug_lines.append(repr(options))
            if options:
                next_dir = random.choice(options)
            else:
                # yield the same as last time, because it doesn't matter
                pass
            yield next_dir
