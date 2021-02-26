import time
import threading

from .board import Board


class Application:
    def __init__(self, window, refresh_rate=30, tick_rate=5, max_shape=None):
        self._stop = False
        self._tick_rate = tick_rate
        self._refresh_rate = refresh_rate
        self._handlers = {}

        shape = window.shape
        if max_shape:
            shape = (
                min(max_shape[0], shape[0]),
                min(max_shape[1], shape[1]),
            )
        self.window = window  # total screen
        self.window.install_handlers(self)

        if max_shape:
            max_shape=(100, 100)
        self.board = Board(self, self.window[0:shape[0], 0:shape[1]-1])
        self.board.install_handlers(self)

    def add_handler(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)

    def stop(self, _):
        self._stop = True

    def start_listener_thread(self):
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def start_render_thread(self):
        self.render_thread = threading.Thread(target=self.render)
        self.render_thread.daemon = True
        self.render_thread.start()

    def run(self):
        self.start_listener_thread()
        self.start_render_thread()

        while not self._stop:
            try:
                self.board.tick()
                time.sleep(1/self._tick_rate)
            except KeyboardInterrupt:
                self.stop(None)

    def handle(self, event):
        for handler in self._handlers.get(event, []):
            handler(event)

    def listen(self):
        for event in self.window.events():
            self.handle(event)

    def render(self):
        while True:
            self.draw()
            self.window.render()
            time.sleep(1//self._refresh_rate)

    def draw(self):
        self.board.draw()