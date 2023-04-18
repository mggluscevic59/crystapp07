import asyncua.sync

from urllib.parse import urlparse

class baseServer:
    def __init__(self) -> None:
        self._server = asyncua.sync.Server()

    @property
    def endpoint(self):
        if self._server.aio_obj.bserver:
            bserver = self._server.aio_obj.bserver
            hostname, port = bserver.hostname, bserver.port
            url = urlparse(f"opc.tcp://{hostname}:{port}")
            return url
        return self._server.aio_obj.endpoint

    @endpoint.setter
    def endpoint(self, value):
        return self._server.set_endpoint(url=value)

    def disable_clock(self):
        self._server.disable_clock()

    def get_namespace_index(self, url:str):
        return self._server.get_namespace_index(url)

    def __del__(self):
        if self._server.tloop.is_alive():
            # if looping, stop the loop
            self._server.tloop.stop() 

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def is_started(self):
        if self._server.aio_obj.bserver:
            return self._server.aio_obj.bserver._server.is_serving()
        return False

    def start(self):
        self._server.start()

    def stop(self):
        if self._server.aio_obj.bserver:
            # if connected, stop connection
            self._server.stop()
        if self._server.tloop.is_alive():
            # if looping, stop the loop
            self._server.tloop.stop() 
