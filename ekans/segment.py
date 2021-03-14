from .drawable import Drawable
from .directions import UP, DOWN, LEFT, RIGHT, UNCH, ALL, get_dir

SEGMENT_CHARS = {
    # in, out
    (LEFT, RIGHT): "═",
    (UP, DOWN): "║",
    (DOWN, RIGHT): "╔",
    (DOWN, LEFT): "╗",
    (UP, RIGHT): "╚",
    (UP, LEFT): "╝",
    (LEFT, UNCH): "╡",
    (RIGHT, UNCH): "╞",
    (UP, UNCH): "╨",
    (DOWN, UNCH): "╥",
}
for (p, n), v in list(SEGMENT_CHARS.items()):
    SEGMENT_CHARS[(n, p)] = v


class Segment(Drawable):
    def __init__(self, board, x, y, d):
        self.board = board
        self.x = x
        self.y = y
        self.d = d

        # fwd means towards lower indices, means towards the head,
        # i.e. the direction of movement.
        self.fwd = None
        self.back = None
        self.snake = None

    @property
    def coord(self):
        return (self.x, self.y)

    @coord.setter
    def coord(self, value):
        self.x, self.y = value

    @property
    def window(self):
        return self.board.window

    def draw(self):
        try:
            char = self.get_char()
        except KeyError:
            char = "?"
        self.window.insstr(self.x, self.y, char, self)

    def get_char(self):
        if self.fwd is self.snake.root:
            return "$"
        delta_key = tuple(
            [
                get_dir(
                    self.fwd.x - self.x if self.fwd is not self.snake.root else 0,
                    self.fwd.y - self.y if self.fwd is not self.snake.root else 0,
                ),
                get_dir(
                    self.back.x - self.x if self.back is not self.snake.root else 0,
                    self.back.y - self.y if self.back is not self.snake.root else 0,
                ),
            ]
        )
        return SEGMENT_CHARS[delta_key]
