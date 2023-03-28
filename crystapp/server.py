import logging
import julabo

from asyncua.sync import Server as SyncServer, ua
from .utility import set_ip, find_node_by_namespace_index, write_props, match_methods, binder

class Server:
    def __init__(self) -> None:
        self._log = logging.getLogger(f"crystapp.{__name__}")
        self._silence = ["asyncua.server.address_space", "asyncua.common.xmlimporter"]
        self._server = None
        self._binded = {}

        self._silence_loggers()
        # default permissive manager + internal session
        self._server = SyncServer()
        # Narrov down security
        self._server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        # public endpoint
        self._server.set_endpoint(f"opc.tcp://{set_ip(True)}:4840")

    # def __del__(self):
    #     if self._server.tloop.is_alive():
    #         self._server.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self._server.start()

    def stop(self):
        self._server.stop()

    def _silence_loggers(self):
        for _log in self._silence:
            logging.getLogger(_log).setLevel(logging.CRITICAL)

    def _connect_driver(self, url):
        args = {
            "url"               : "tcp://178.238.237.121:5050",
            # "url"               : f"tcp://{url}:5050",
            "concurrency"       : "syncio",
            "auto_reconnect"    : True
        }
        device = julabo.JulaboCF(julabo.connection_for_url(**args))
        # not to be binded from device
        _excluded = ["__","write"]
        for name in dir(device):
            # is method
            if callable(bound := getattr(device, name)):
                # not containing forbiden characters
                if not any(x in name for x in _excluded):
                    # setattr(self, name, bound)
                    self._binded[name] = bound

    def populate(self, types_path, devices_path:list):
        self._server.import_xml(types_path)
        for path in devices_path:
            self._server.import_xml(path)

        all_namespaces = self._server.get_namespace_array()
        # TODO: implement better solution -> pop without popping
        last_namespace = all_namespaces[len(all_namespaces)-1]
        idx = self._server.get_namespace_index(last_namespace)
        device = find_node_by_namespace_index(idx, self)

        write_props(device)
        
        self._connect_driver(last_namespace)
        for node, method in match_methods(device, self._binded):
            self._server.link_method(node, binder(method))
