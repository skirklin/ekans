import os
from .app import Application
from .window import CursesWindow, VirtualWindow

def get_max_shape():
    env_shape = os.environ.get("EKANS_SHAPE", "40x40")
    return tuple(map(int, env_shape.split("x")))

def play(level="Bars()", seed=None):
    with CursesWindow() as window:
        app = Application(window, max_shape=get_max_shape(), level=level)
        controller = window.controller(tick_rate=5)
        controller.run(app)
        return app

def score(name, level="Bars()", n=30, seed=None):
    from multiprocessing import Pool

    if n > 1:
        with Pool() as p:

            results = [p.apply_async(ai, (name,), {"headless": True, "level": level}) for i in range(n)]
            apps = [r.get() for r in results]
    else:
        apps = [
            ai(name, headless=True)
        ]
    
    total_score = sum(app['score'] for app in apps)
    total_turns = sum(app['turns'] for app in apps)
    board = apps[0]['board']  # if adding random barriers, need to change
    total_size = len([c for c in board if c not in ("\n", "#")])
    print()
    print(f"average score: {total_score/len(apps)} (or {100*total_score/len(apps)/total_size:.2f})")
    print(f"average game length: {total_turns/len(apps):.2f}")
    print(f"total turns: {total_turns}")
    print(f"total score: {total_score}")

def ai(name, level="Bars()", headless=False, seed=None):
    import ekans.controllers.ai

    if headless:
        window_func = lambda: VirtualWindow(get_max_shape())
    else:
        window_func = lambda: CursesWindow()

    with window_func() as window:
        app = Application(window, max_shape=get_max_shape(), level=level)

        Controller = getattr(ekans.controllers.ai, name)
        controller = Controller(0, block=not headless)
        controller.run(app)
        return {"score": app.board.snake.score, "turns": app.board.snake.turn, "board": str(app.board.window)}