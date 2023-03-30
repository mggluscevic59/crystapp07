import logging
import subprocess
import time

from pathlib import Path
from .utility import kill
FMT = "%(asctime)-15s %(levelname)-5s %(name)s: %(message)s"

class JulaboMock:
    def __init__(self, environment, fixture) -> None:
        self._log = logging.getLogger(__name__)
        self._env = Path(environment)
        self._fxtr = Path(fixture)
        self._cmd = [
            f"{self._env.absolute()}/bin/python3.10",
            f"{self._env.absolute()}/bin/sinstruments-server",
            "-c",
            str(self._fxtr.absolute()),
            "--log-level",
            logging.getLevelName(self._log.getEffectiveLevel())
        ]

        self._spawn = None

    def start(self):
        if self.is_started():
            self._log.info("process already started!")
            return
        self._spawn = subprocess.Popen(self._cmd)
        # HACK: give time to do
        time.sleep(.27)

    def stop(self):
        self._spawn.terminate()
        if self.is_started():
            self._log.info("exiting...")
            try:
                self._spawn.wait(timeout=3)
            except subprocess.TimeoutExpired:
                kill(self._spawn.pid)

    def is_started(self):
        if self._spawn and not self._spawn.poll():
            return True
        return False

    def __enter__(self):
        self.start()
        return self

    def  __exit__(self, exception_type, exception_value, exception_traceback):
        self.stop()
