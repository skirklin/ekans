import abc

class Drawable(abc.ABC):
    @abc.abstractmethod
    def draw(self, scr):
        pass