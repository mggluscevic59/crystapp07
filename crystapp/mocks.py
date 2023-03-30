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
        self._cmd = Path(fixture)
        self._spawn = None

    def start(self):
        if not self._spawn:
            cmd_list = [ f"{self._env.absolute()}/bin/python3.10",
              f"{self._env.absolute()}/bin/sinstruments-server",
                "-c",
                str(self._cmd.absolute()),
                "--log-level",
                logging.getLevelName(self._log.getEffectiveLevel())
                ]
            # cmd_string = " ".join(cmd_list)
            self._spawn = subprocess.Popen(cmd_list)
            # HACK: give time to do
            time.sleep(.25)

    def stop(self):
        self._spawn.terminate()
        try:
            self._spawn.wait(timeout=3)
        except subprocess.TimeoutExpired:
            kill(self._spawn.pid)
        self._log.info("exiting...")

    def __enter__(self):
        self.start()
        return self

    def  __exit__(self, exception_type, exception_value, exception_traceback):
        self.stop()
