import abc


class Player(abc.ABC):
    def __init__(self, snake):
        self.snake = snake
        self.board = snake.board
        self.app = snake.app

    def get_direction(self):
        pass