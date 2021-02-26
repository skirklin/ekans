import asyncio
import random

from .drawable import Drawable
from .segment import Segment
from .directions import LEFT, RIGHT, UP, DOWN


class Snake(Drawable):
    def __init__(self, direction):
        self.direction = direction

        self.root = Segment(None, None)
        self.root.back = self.root
        self.root.fwd = self.root
        self.length = 0
        
    def move(self):
        # move tail to in front of head
        tail = self.tail
        head = self.head
        self._remove(self.tail)
        tail.x = head.x + self.direction.dx
        tail.y = head.y + self.direction.dy
        self.insert(0, tail)

    async def run(self):
        while True:
            self.move()
            await asyncio.sleep(0.5)


    @classmethod
    def Make(cls, x, y, size=8):
        s = cls(UP)
        s.append(Segment(x, y))
        for _ in range(size - 1):
            s.append_segment(DOWN)
        return s

    def get_char(self):
        return "$"

    def draw(self, scr):
        for segment in self:
            segment.draw(scr)

    @property
    def head(self):
        return self[0]

    @property
    def tail(self):
        return self[-1]

    def prepend(self):
        head = self.head
        new_seg = Segment(
            head.x + self.direction.dx,
            head.y + self.direction.dy,
        )
        self.insert(0, new_seg)


    def append_segment(self, direction):
        tail = self.tail
        
        new_seg = Segment(
            tail.x + direction.dx,
            tail.y + direction.dy,
        )
        self.append(new_seg)

    def __iter__(self):
        n = self.root.back
        while n is not self.root:
            yield n
            n = n.back

    def __getitem__(self, idx):
        return list(self)[idx]

    def append(self, seg):
        assert isinstance(seg, Segment), seg
        self._insert_after(self.root.fwd, seg)

    def _insert_after(self, fwd, curr):
        assert curr.snake is None, curr.snake
        curr.snake = self
        _next = fwd.back
        # 4 references to update: 2 on curr, 1 each for fwd and back
        curr.back = fwd.back
        fwd.back = curr
        curr.fwd = fwd
        _next.fwd = curr
        self.length += 1

    def _remove(self, seg):
        assert seg is not self.root, seg
        seg.snake = None
        seg.fwd.back = seg.back
        seg.back.fwd = seg.fwd
        self.length -= 1

    def insert(self, i, seg):
        assert isinstance(seg, Segment), seg
        if i <= -self.length or i >= self.length:
            raise IndexError(i)

        n = self.root
        while i != 0:
            if i > 0:
                n = n.back
                i -= 1
            else:
                n = n.fwd
                i += 1
                
        self._insert_after(n, seg)

    def remove(self, i):
        n = self.root.back
        while i > 0:
            n = n.back
            i -= 1
        self._remove(n)
