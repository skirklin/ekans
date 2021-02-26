import time
import asyncio
import threading


from .board import Board


class Application:
    def __init__(self, window, refresh_rate=30):
        self.stop = False
        self.refresh_rate = refresh_rate
        self.window = window

    def start(self):
        self.board = Board(self.window)
        asyncio.run(self.run())

    async def run(self):

        t = threading.Thread(target=self.listen)
        t.daemon = True
        t.start()

        asyncio.create_task(self.board.run())
        while True:
            self.board.draw(self.window)
            self.window.render()
            self.window.logfile.write("updated\n")
            await asyncio.sleep(1 / self.refresh_rate)

    def listen(self):
        for event in self.window.events():
            print(event)

    def draw(self, window):
        self.board.draw(window)
        window.refresh()