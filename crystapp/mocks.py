import logging
import subprocess

from pathlib import Path

class JulaboMock:
    def __init__(self, environment, fixture) -> None:
        self._environment = environment
        self._path = fixture
        self._log = logging.getLogger(f"crystapp.{__name__}")
        self._spawn = None

    def __del__(self):
        # close ports!
        if self._spawn:
            self.stop()

    def start(self):
        # activate environment
        env = Path(f"{self._environment}/bin/activate")
        subprocess.run(f"source {env.absolute()}", shell=True)
        if not self._spawn:
            cmd = f"sinstruments-server --log-level=INFO {self._path}"
            self._spawn = subprocess.Popen(cmd, shell=True)
        return self

    def stop(self):
        self._spawn.terminate()
