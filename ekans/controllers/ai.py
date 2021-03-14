import time
import random
import numpy as np
import json

import abc

from .base import HeadlessController
from .. import vision
from ..barrier import Barrier
from ..segment import Segment
from ..directions import KEY_MAP, DIR_MAP
from ..events import ADD_APPLE, REMOVE_APPLE


class AIController(HeadlessController):
    def get_allowed_directions(self, app):
        return list(app.board.snake.allowed_moves())

    @abc.abstractmethod
    def pick_direction(self, app, options):
        pass


class RandomAIController(AIController):
    def pick_direction(self, app, options):
        if not options:
            return DIR_MAP[app.board.snake.head.d]
        return random.choice(options)

    def events(self, app):
        yield " "
        while not app.board.game_is_over():
            options = self.get_allowed_directions(app)
            next_dir = self.pick_direction(app, options)
            app.debug_lines.append(next_dir)
            yield next_dir


class PartitionConstraint(AIController):
    def run(self, app):
        self.partitioning = vision.Partition(app.board)
        super().run(app)

    def get_allowed_directions(self, app):
        self.partitioning.compute()
        snake = app.board.snake
        segments = {}
        for k, d in snake.allowed_moves().items():
            pi, pj = snake.peek(d)
            sid = self.partitioning.segmentation[pi, pj]
            if sid != 0:
                segments[k] = sid

        if not segments:
            return []

        count = lambda sid: (self.partitioning.segmentation == sid).sum()

        sizes = {s: count(s) for s in set(segments.values())}
        if all(v > len(snake) for v in sizes.values()):
            return [k for k in KEY_MAP if k in segments]
        return [
            k
            for k in KEY_MAP
            if k in segments and sizes[segments[k]] == max(sizes.values())
        ]


class NaiveAIController(PartitionConstraint, RandomAIController):
    pass


class HungryOptimizer(RandomAIController):
    def run(self, app):
        self.field = vision.field(app.board)
        super().run(app)

    def get_handlers(self):
        return {
            ADD_APPLE: self._update_gradient_add,
            REMOVE_APPLE: self._update_gradient_remove,
        }

    def _update_gradient_add(self, app, event, payload):
        vision.update_apple_field(app.board.window, payload["apple"], self.field, 1)

    def _update_gradient_remove(self, app, event, payload):
        vision.update_apple_field(app.board.window, payload["apple"], self.field, -1)

    def pick_direction(self, app, options):
        snake = app.board.snake
        coord = snake.head.coord
        grad_x, grad_y = np.gradient(self.field)

        def tgt_func(k):
            d = KEY_MAP[k]
            g = [
                grad_x[coord],
                grad_y[coord],
            ]
            return -np.dot(g, [d.dx, d.dy])

        scores = {k: tgt_func(k) for k in options}
        if not scores:
            return DIR_MAP[snake.head.d]

        if self._audit_log:
            self.record(
                options=scores,
                window=str(snake.window),
            )
        return min(scores, key=lambda x: scores[x])


class HungryAIController(HungryOptimizer, PartitionConstraint):
    pass