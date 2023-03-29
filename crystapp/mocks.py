import logging
import subprocess
# import psutil
import time
# import sys

from pathlib import Path

FMT = "%(asctime)-15s %(levelname)-5s %(name)s: %(message)s"
# logging.basicConfig(format=FMT)

# def kill(proc_pid):
#     process = psutil.Process(proc_pid)
#     for proc in process.children(recursive=True):
#         proc.kill()
#     process.kill()

class JulaboMock:
    def __init__(self, environment, fixture) -> None:
        self._log = logging.getLogger(__name__)
        self._env = Path(environment)
        self._cmd = Path(fixture)
        self._spawn = None

        # self.set_formatter()

    # def __del__(self):
    #     self.stop()

    # def set_formatter(self):
    #     fmt = "%(asctime)-15s %(levelname)-5s %(name)s: %(message)s"
    #     logger_handler = logging.StreamHandler()
    #     self._log.addHandler(logger_handler)
    #     self._log.setLevel(logging.DEBUG)
    #     logger_handler.setFormatter(logging.Formatter(fmt))
    #     self._log.info(self._log.handlers)
        # self._log.handlers[0].setFormatter(logging.Formatter(fmt))
        # handler = logging.StreamHandler()
        # handler.setLevel(logging.DEBUG)
        # formatter = logging.Formatter(fmt)
        # handler.setFormatter(formatter)
        # formatter = logging.Formatter(fmt)
        # ch = logging.StreamHandler()
        # ch.setFormatter(formatter)
        # self._log.addHandler(handler)

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
            # FIXME: _warn("subprocess %s is still running" % self.pid
            self._spawn = subprocess.Popen([cmd_string], shell=True)
            # hack: give time to do
            time.sleep(1)

    def stop(self):
        self._spawn.terminate()
        self._log.info("exiting...")
        # try:
        #     self._spawn.wait(timeout=3)
        # except subprocess.TimeoutExpired:
        #     kill(self._spawn.pid)

    def __enter__(self):
        self.start()
        return self

    def  __exit__(self, exception_type, exception_value, exception_traceback):
        self.stop()
