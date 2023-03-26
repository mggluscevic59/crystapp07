import logging

from sinstruments.simulator import create_server_from_config, StreamServer

class Mock:
    def __init__(self) -> None:
        self._config = None
        self._path = None
        self._server = None

    @property
    def configuration(self):
        if self._config:
            return self._config
        raise FileNotFoundError("Configuration not set!")

    @configuration.setter
    def configuration(self, value):
        self._config = value

    def start(self):
        if not self._server:
            self._server = create_server_from_config(self.configuration)
        self._server.start()
        return self

    def stop(self):
        # greenlet stop for nothing to do!
        self._server.stop()
