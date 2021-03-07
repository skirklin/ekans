import time
import threading

from .board import Board


# TODOS:
#  - handle pane resizing
#  - start/stop/pause
#  - score keeping
#  - virtualized play for adding AI strategies


class Application:
    def __init__(self, window, refresh_rate=5, tick_rate=5, max_shape=None):
        self._stop = False
        self._tick_rate = tick_rate
        self._refresh_rate = refresh_rate
        self._handlers = {}
        self._next_tick = 0
        self.max_shape = max_shape

        self.debug_console_height = 3
        self.debug_lines = []
        self.children = []

        self.window = window  # total screen
        self.window.install_handlers(self)
        self.setup_board()

    def setup_board(self):
        shape = self.window.shape
        max_shape = self.max_shape
        if max_shape:
            shape = (
                min(self.max_shape[0], shape[0]),
                min(self.max_shape[1], shape[1]),
            )
        
        # top line as app status line
        # bottom line as game status line
        status_height = 1
        self.board = Board(
            self,
            self.window[0 : shape[0], self.debug_console_height : shape[1] - status_height],
        )
        self.board.install_handlers(self)
        self.board.pause()


    def set_status(self, msg):
        console = msg.ljust(self.window.shape[0])
        self.window.addstr(0, -1, console, None)

    def add_handler(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)

    def remove_handler(self, event, handler):
        try:
            handlers = self._handlers[event]
        except KeyError:
            self.debug_lines.append(f"Cannot remove handler for unknown event {event}")
        else:
            try:
                handlers.remove(handler)
            except ValueError:
                self.debug_lines.append(f"Cannot remove {handler} from {event}, it isn't registered")


    def stop(self, event=None):
        self._stop = True
        self.render_thread.join()

    def start_listener_thread(self):
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def start_render_thread(self):
        self.render_thread = threading.Thread(target=self.render)
        self.render_thread.start()

    def render(self):
        while not self._stop:
            self.draw()
            self.window.render()
            time.sleep(1 // self._refresh_rate)

    def run(self):
        self.start_listener_thread()
        self.start_render_thread()

        while not self._stop:
            try:
                t = time.time()
                if t > self._next_tick:
                    self.tick()
                time.sleep(1 / self._refresh_rate)
            except KeyboardInterrupt:
                self.stop()

    def handle(self, event):
        for handler in self._handlers.get(event, []):
            handler(event)

    def listen(self):
        for event in self.window.events():
            self.debug_lines.append(f"EVENT: {event}")
            self.handle(event)

    def draw(self):
        self.window.clear()
        for child in self.children:
            child.draw()
        self.board.draw()
        self._draw_status()
        self._draw_debug()

    def _draw_status(self):
        # Some board state is not rendered in the board, but the App may choose to present it
        statusline = self.board.status.ljust(self.window.shape[0])
        self.window.addstr(0, -1, statusline, None)

    def _draw_debug(self):
        for i, line in enumerate(self.debug_lines[-self.debug_console_height:]):
            dl = line.ljust(self.window.shape[0])
            self.window.addstr(0, i, dl, None)
            

    def tick(self):
        self.board.tick()
        self._next_tick = time.time() + 1 / self._tick_rate
