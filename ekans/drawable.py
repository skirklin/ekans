import abc


class Drawable(abc.ABC):
    def __init__(self, app):
        self.app = app
        
    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def events(self):
        pass

    def install_handlers(self):
        for k, v in self.events().items():
            self.app.add_handler(k, v)

    def remove_handlers(self):
        for k, v in self.events().items():
            self.app.remove_handler(k, v)