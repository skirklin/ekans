"""
Dead end detection.
"""

import numpy as np
import collections

from .barrier import Barrier
from .segment import Segment
from .apple import Apple
from . import directions


class Partition:
    def __init__(self, snake, board):
        self.snake = snake
        self.board = board
        self.segmentation = np.zeros(board.window.shape, dtype=int)
        self.last_turn = snake.turn

    def compute(self, avoid=None):
        curr_id = 1
        window = self.board.window
        avoid = avoid or []

        id_to_idx = collections.defaultdict(set)
        seg = self.segmentation
        seg[:] = 0

        for i in range(window.shape[0]):
            for j in range(window.shape[1]):
                if (i, j) in avoid:
                    continue
                if type(window.objects[i, j]) in (Barrier, Segment):
                    continue

                back = seg[i - 1, j] if i > 0 else 0
                up = seg[i, j - 1] if j > 0 else 0
                if up or back:
                    if up and back and up != back:
                        coords = id_to_idx.pop(up)
                        for ii, jj in coords:
                            seg[ii, jj] = back
                        id_to_idx[back] |= coords
                        seg_id = back
                    else:
                        seg_id = up or back
                else:
                    seg_id = curr_id
                    curr_id += 1
                seg[i, j] = seg_id
                id_to_idx[seg_id].add((i, j))
        return seg

    def update(self):
        # to be valid, must be called between _every_
        snake = self.snake
        if snake.turn == self.last_turn:
            return
        elif snake.turn != self.last_turn + 1:
            raise Exception("Incremental partitioning missed update")

        head = snake.head
        # look for T junctions
        c = snake.check_dir
        if c(head.forward) and not c(head.forward.left) and c(head.forward.right):
            pass



def update_apple_field(window, apple, accum, sign=1):
    dx = window.coords[0] - apple.x
    dy = window.coords[1] - apple.y
    accum += sign / ((dy ** 2 + dx ** 2) ** 0.5 + 1e-9)

def field(board, out=None):
    window = board.window
    apples = board.apples
    if out is None:
        p = np.zeros(window.shape, dtype=float)
    else:
        p = out
        p[:] = 0.0

    for apple in apples:
        update_apple_field(window, apple, p)
    return p