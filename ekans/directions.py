import collections

__all__ = ["UP", "DOWN", "LEFT", "RIGHT", "UNCH", "ALL", "get_dir"]

class Direction:
    __slots__ = ["name", "dx", "dy", "left", "right", "back"]
    def __init__(self, name, dx, dy):
        self.name = name
        self.dx = dx
        self.dy = dy

UP = Direction("UP", 0, -1)
DOWN = Direction("DOWN", 0, 1)
LEFT = Direction("LEFT", -1, 0)
RIGHT = Direction("RIGHT", 1, 0)
UNCH = Direction("UNCH", 0, 0)

UP.left, UP.right, UP.back = LEFT, RIGHT, DOWN
LEFT.left, LEFT.right, LEFT.back = DOWN, UP, RIGHT
DOWN.left, DOWN.right, DOWN.back = RIGHT, LEFT, UP
RIGHT.left, RIGHT.right, RIGHT.back = UP, DOWN, LEFT


ALL = {UP, DOWN, LEFT, RIGHT, UNCH}
LOOKUP = {(d.dx, d.dy): d for d in ALL}


KEY_MAP = {
    "KEY_LEFT": LEFT,
    "KEY_UP": UP,
    "KEY_RIGHT": RIGHT,
    "KEY_DOWN": DOWN,
}

DIR_MAP = {
    d: k for k, d in KEY_MAP.items()
}

def get_dir(dx, dy):
    return LOOKUP[dx, dy]
