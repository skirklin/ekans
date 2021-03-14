import abc
import time
import os
import json

class Controller(abc.ABC):
    @abc.abstractmethod
    def run(self, app):
        pass


class HeadlessController(Controller):
    def __init__(self, wait=0, block=False):
        self.wait = wait
        self.block = block
        if audit_log := os.environ.get("EKANS_AUDIT_LOG"):
            self._audit_events = []
            self._audit_log = open(audit_log, 'w')
        else:
            self._audit_events = []
            self._audit_log = None

    def record(self, **kwargs):
        self._audit_events.append(kwargs)

    @abc.abstractmethod
    def events(self, app):
        pass

    def get_handlers(self):
        return {}

    def install_handlers(self, app):
        for event, handler in self.get_handlers().items():
            app.add_handler(event, handler)
    
    def remove_handlers(self, app):
        for event, handler in self.get_handlers().items():
            app.remove_handler(event, handler)

    def run(self, app):
        try:
            self.install_handlers(app)
            self._run(app)

        finally:
            self.remove_handlers(app)

    def _run(self, app):
        for event in self.events(app):
            app.handle(event)
            app.tick()
            if self.wait:
                time.sleep(self.wait)
            app.draw()
        if self.block:
            while True:
                time.sleep(1)

        if self._audit_log:
            json.dump(self._audit_events, self._audit_log, indent=2, sort_keys=True)