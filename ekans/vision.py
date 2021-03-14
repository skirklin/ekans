"""
Dead end detection.
"""

import numpy as np
import collections

from .barrier import Barrier
from .segment import Segment
from .apple import Apple


def partition(board, out=None):
    curr_id = 1
    window = board.window

    id_to_idx = collections.defaultdict(set)
    if out is None:
        seg = np.zeros(window.shape, dtype=int)
    else:
        seg = out
        seg[:] = 0

    for i in range(window.shape[0]):
        for j in range(window.shape[1]):
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