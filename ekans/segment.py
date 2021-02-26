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
    def __init__(self, x, y):
        self.x = x
        self.y = y

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

    def fwd_dir(self):
        if self.back is None:
            return self.snake.direction
        return get_dir(
            self.back.x - self.x,
            self.back.y - self.y,
        )

    def back_dir(self):
        if self.fwd is None:
            return UNCH
        return get_dir(
            self.fwd.x - self.x,
            self.fwd.y - self.y,
        )

    def check(self):
        assert self.back
        assert self.fwd
        assert self.fwd_dir() in ALL
        assert self.back_dir() in ALL

    def draw(self, window):
        try:
            char = self.get_char()
        except KeyError:
            char = "?"
        window.insstr(self.x, self.y, char)

    def get_char(self):
        if self.fwd is self.snake.root:
            return "$"
        delta_key = tuple(
            [
                get_dir(
                    self.fwd.x - self.x
                    if self.fwd is not self.snake.root
                    else 0,
                    self.fwd.y - self.y
                    if self.fwd is not self.snake.root
                    else 0,
                ),
                get_dir(
                    self.back.x - self.x
                    if self.back is not self.snake.root
                    else 0,
                    self.back.y - self.y
                    if self.back is not self.snake.root
                    else 0,
                ),
            ]
        )
        return SEGMENT_CHARS[delta_key]
