import time
import random

from .base import HeadlessController

from ..directions import KEY_MAP

class AIController(HeadlessController):
    def __init__(self, wait=0, block=False):
        self.block = block
        self.wait = wait

    def events(self, app):
        yield " "
        while not app.board.game_is_over():
            next_dir = random.choice(list(KEY_MAP.keys()))
            yield next_dir