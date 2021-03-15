import time
import numpy as np
import json

import abc

from .base import HeadlessController
from .. import pathing
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
        return app.random.choice(options)

    def events(self, app):
        yield " "
        while not app.board.game_is_over():
            options = self.get_allowed_directions(app)
            next_dir = self.pick_direction(app, options)
            app.debug_lines.append(next_dir)
            yield next_dir


class PartitionConstraint(AIController):
    def run(self, app):
        self.partitioning = pathing.Partition(app.board)
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

class AvoidPartitioning(PartitionConstraint):
    def get_allowed_directions(self, app):
        max_sid = len(np.unique(self.partitioning.compute()))

        snake = app.board.snake
        segments = {}
        for k, d in snake.allowed_moves().items():

            pi, pj = snake.peek(d)
            sid = self.partitioning.segmentation[pi, pj]
            if sid != 0:
                segments[k] = sid

        count = lambda sid: (self.partitioning.segmentation == sid).sum()

        if not segments:
            return []

        sizes = {s: count(s) for s in set(segments.values())}

        partition_conserving_segments = {}
        app.debug_lines.append(f"segments: {segments}")
        for k, sid in segments.items():
            pi, pj = snake.peek(KEY_MAP[k])
            this_max_sid = len(np.unique(self.partitioning.compute(avoid=[(pi, pj)])))
            if max_sid and this_max_sid > max_sid:
                app.debug_lines.append(f"avoiding {k} because it creates a partition (max_sid={max_sid}, this_max_sid={this_max_sid}")
                continue

            partition_conserving_segments[k] = sid

        key_to_size = {k: sizes[sid] for k, sid in segments.items()}
        app.debug_lines.append(f"pc segs: {partition_conserving_segments}")
        app.debug_lines.append(f"segment sizes: {key_to_size}")
        if partition_conserving_segments:
            pc_sizes = {sid: size for sid, size in sizes.items() if sid in partition_conserving_segments.values()}
            if any([v > len(snake) for v in pc_sizes.values()]):
                segments = partition_conserving_segments
                sizes = pc_sizes
        
        sizes = {sid: size for sid, size in sizes.items() if sid in segments.values()}
        if all([v > len(snake) for v in sizes.values()]):
            return list(segments.keys())
        return [
            k
            for k in segments
            if sizes[segments[k]] == max(sizes.values())
        ]


class NaiveAIController(PartitionConstraint, RandomAIController):
    pass


class HungryOptimizer(RandomAIController):
    def run(self, app):
        self.field = pathing.field(app.board)
        super().run(app)

    def get_handlers(self):
        return {
            ADD_APPLE: self._update_gradient_add,
            REMOVE_APPLE: self._update_gradient_remove,
        }

    def _update_gradient_add(self, app, event, payload):
        pathing.update_apple_field(app.board.window, payload["apple"], self.field, 1)

    def _update_gradient_remove(self, app, event, payload):
        pathing.update_apple_field(app.board.window, payload["apple"], self.field, -1)

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
            app.debug_lines.append("No options, returning forward")
            return DIR_MAP[snake.head.d]

        if self._audit_log:
            self.record(
                options=scores,
                window=str(snake.window),
            )
        return min(scores, key=lambda x: scores[x])


class HungryAIController(HungryOptimizer, AvoidPartitioning):
    pass

