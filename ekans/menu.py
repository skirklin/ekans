from .drawable import Drawable
from .directions import UP, DOWN


class Menu(Drawable):
    def __init__(self, app, items):
        self.app = app
        assert isinstance(items, list)
        assert all(isinstance(v, tuple) for _, v in items)
        assert all(isinstance(k, str) for k, _ in items)
        self.items = items


    def events(self):
        return {
            DOWN: self._menu_down,
            UP, self._menu_up,
        }