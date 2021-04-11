import abc
import time
import threading

from .base import Controller


class InteractiveController(Controller):
    def __init__(self, window):
        self.window = window

    def run(self, app):
        app.run_realtime()
        while not app.is_stopped():
            try:
                event = self.window.stdscr.getkey()
                app.debug_lines.append(f"event: {event}")
                with self.window.lock:
                    app.handle(event)
            except KeyboardInterrupt:
                app.stop()