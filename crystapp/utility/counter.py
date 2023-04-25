class Counter:
    def __init__(self) -> None:
        self._counter = 0

    def wait(self):
        if self._counter < 4:
            self._counter += 1
            return
        self._counter = 0
        print(".", end="", flush=True)
