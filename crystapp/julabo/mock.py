import logging

from sinstruments.pytest import server_context

class Mock:
    def __init__(self, configuration) -> None:
        self._log = logging.getLogger(__name__)
        self._spawn = server_context(configuration)

    def start(self):
        # BUG: check if old logic applies
        if self.is_started():
            self._log.info("process already started!")
            return
        self._spawn.start()

    def stop(self):
        self._spawn.stop()

    def is_started(self):
        if self._spawn.thread is not None and self._spawn.thread.is_alive():
            return True
        return False

    def __enter__(self):
        self.start()
        return self._spawn.server

    def  __exit__(self, exception_type, exception_value, exception_traceback):
        self.stop()
