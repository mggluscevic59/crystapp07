import logging
# import time

# from subprocess import Popen, TimeoutExpired
# from pathlib import Path
# from ..utility import kill
from sinstruments.pytest import server_context

class Mock:
    def __init__(self, configuration) -> None:
        self._log = logging.getLogger(__name__)
        self._spawn = None
        # self._env = Path(environment)
        # self._fxtr = Path(fixture)

    def start(self):
        pass
        # cmd = [
        #     f"{self._env.absolute()}/bin/python3.10",
        #     f"{self._env.absolute()}/bin/sinstruments-server",
        #     "-c",
        #     str(self._fxtr.absolute()),
        #     "--log-level",
        #     logging.getLevelName(self._log.getEffectiveLevel())
        # ]

        # if self.is_started():
        #     self._log.info("process already started!")
        #     return
        # self._spawn = Popen(cmd)
        # # HACK: give time to do
        # time.sleep(.27)

    def stop(self):
        pass
        # self._spawn.terminate()
        # if self.is_started():
        #     self._log.info("exiting...")
        #     try:
        #         self._spawn.wait(timeout=3)
        #     except TimeoutExpired:
        #         kill(self._spawn.pid)

    def is_started(self):
        pass
        # if self._spawn and not self._spawn.poll():
        #     return True
        # return False

    def __enter__(self):
        pass
        # self.start()
        # return self

    def  __exit__(self, exception_type, exception_value, exception_traceback):
        pass
        # self.stop()
