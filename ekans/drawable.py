import abc

class Drawable(abc.ABC):
    @abc.abstractmethod
    def draw(self, window):
        pass