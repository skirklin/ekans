import random

from .drawable import Drawable
from .segment import Segment
from .barrier import Barrier
from .apple import Apple
from .directions import LEFT, RIGHT, UP, DOWN

KEY_MAP = {
    "KEY_LEFT": LEFT,
    "KEY_UP": UP,
    "KEY_RIGHT": RIGHT,
    "KEY_DOWN": DOWN,
}


class Snake(Drawable):
    def __init__(self, direction, board):
        self.direction = direction
        self.board = board
        self.score = 0

        self.root = Segment(None, None, None)
        self.root.back = self.root
        self.root.fwd = self.root
        self.length = 0

    @property
    def window(self):
        return self.board.window

    def move(self):
        # move tail to in front of head
        tail = self.tail
        self._remove(self.tail)
        tail.x, tail.y = self.peek()
        self.insert(0, tail)

    def peek(self):
        head = self.head
        x = head.x + self.direction.dx
        y = head.y + self.direction.dy
        return (x, y)

    def set_direction(self, key):
        direction = KEY_MAP[key]
        back = self.head.back_dir()
        if direction != back:
            self.direction = direction
        self.board.app.tick()

    def install_handlers(self, app):
        for key in KEY_MAP:
            app.add_handler(key, self.set_direction)

    def remove_handlers(self, app):
        for key in KEY_MAP:
            app.remove_handler(key, self.set_direction)

    def tick(self):
        peek = self.peek()
        hit = self.window.get_obj(*peek)
        if isinstance(hit, Apple):
            self.score += 1
            self.board.apples.remove(hit)
            self.grow_forward()
        elif isinstance(hit, (Barrier, Segment)):
            self.board.game_over()
        else:
            self.move()

    @classmethod
    def Make(cls, board, x, y, size=8):
        s = cls(UP, board)
        s.append(s.new_segment(x, y))
        for _ in range(size - 1):
            s.grow_backward([DOWN, RIGHT])
        return s

    def new_segment(self, x, y):
        return Segment(self.board, x, y)

    def get_char(self):
        return "$"

    def draw(self):
        for segment in self:
            segment.draw()

    @property
    def head(self):
        return self[0]

    @property
    def tail(self):
        return self[-1]

    def grow_forward(self):
        head = self.head
        new_seg = self.new_segment(
            head.x + self.direction.dx,
            head.y + self.direction.dy,
        )
        self.insert(0, new_seg)

    def grow_backward(self, directions):
        tail = self.tail

        for direction in directions:
            next_pos = (tail.x + direction.dx, tail.y + direction.dy)
            if next_pos not in self.window:
                continue

            hit = self.window.get_obj(*next_pos)
            if hit is None:
                new_seg = self.new_segment(
                    tail.x + direction.dx,
                    tail.y + direction.dy,
                )
                break
        else:
            raise Exception("Unable to append segment, ran into window borders")
        self.append(new_seg)

    def __iter__(self):
        n = self.root.back
        while n is not self.root:
            yield n
            n = n.back

    def __getitem__(self, idx):
        return list(self)[idx]

    def __len__(self):
        return self.length

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
