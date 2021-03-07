import abc
import time
import threading

from .base import Controller


class KeyboardController(Controller):
    def __init__(self, window, tick_rate=5):
        self.window = window
        self._tick_rate = tick_rate

    def run(self, app):
        self.run_realtime(app)
        while not app.is_stopped():
            try:
                event = self.window.stdscr.getkey()
                app.handle(event)
            except KeyboardInterrupt:
                app.stop()

    def run_realtime(self, app):
        t = threading.Thread(target=self.realtime_loop, args=(app,))
        t.setDaemon(True)
        t.start()

    def realtime_loop(self, app):
        interval = 1 / self._tick_rate
        while not app.is_stopped():
            time.sleep(1 / self.window._refresh_rate)
            if time.time() - app._last_tick > interval:
                app.tick()
