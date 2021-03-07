import collections

__all__ = ["UP", "DOWN", "LEFT", "RIGHT", "UNCH", "ALL", "get_dir"]

Direction = collections.namedtuple("Direction", ["name", "dx", "dy"])

UP = Direction("UP", 0, -1)
DOWN = Direction("DOWN", 0, 1)
LEFT = Direction("LEFT", -1, 0)
RIGHT = Direction("RIGHT", 1, 0)
UNCH = Direction("UNCH", 0, 0)

ALL = {UP, DOWN, LEFT, RIGHT, UNCH}
LOOKUP = {(d.dx, d.dy): d for d in ALL}


KEY_MAP = {
    "KEY_LEFT": LEFT,
    "KEY_UP": UP,
    "KEY_RIGHT": RIGHT,
    "KEY_DOWN": DOWN,
}


def get_dir(dx, dy):
    return LOOKUP[dx, dy]
