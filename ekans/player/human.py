from .base import Player

class HumanPlayer(Player):
    def __init__(self, snake, window):
        super().__init__(snake)
        self.window = window

    @classmethod
    def Factory(cls, window):
        return lambda snake: cls(snake, window)

    def get_direction(self):
        # the snake's current direction is updated by callbacks, so just go where it is pointed.
        return self.snake.direction