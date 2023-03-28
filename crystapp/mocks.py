import logging
import subprocess
import psutil

from pathlib import Path

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

class JulaboMock:
    def __init__(self, environment, fixture) -> None:
        self._log = logging.getLogger(f"crystapp.{__name__}")
        self._env = Path(environment)
        self._cmd = Path(fixture)
        self._spawn = None

    # def __del__(self):
    #     self.stop()

    def start(self):
        if not self._spawn:
            cmd_list = [ "source",
                f"{self._env.absolute()}/bin/activate;",
                "sinstruments-server",
                "-c",
                str(self._cmd.absolute()),
                "--log-level",
                logging.getLevelName(self._log.getEffectiveLevel())
                ]
            cmd_string = " ".join(cmd_list)
            self._spawn = subprocess.Popen([cmd_string], shell=True)

    def stop(self):
        self._spawn.terminate()
        try:
            self._spawn.wait(timeout=3)
        except subprocess.TimeoutExpired:
            kill(self._spawn.pid)

    def __enter__(self):
        self.start()
        return self

    def  __exit__(self, exception_type, exception_value, exception_traceback):
        self.stop()
