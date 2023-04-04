import logging
import asyncua.sync

from asyncua.sync import SyncNode, ua
from .julabo.driver import Driver
from .utility import silence_loggers, find_object_type

# logging level: critical for noisy loggers
banned_loggers = [
    "asyncua.server.address_space",
    "asyncua.common.xmlimporter",
    "asyncua.server.uaprocessor"
    ]
silence_loggers([logging.getLogger(x) for x in banned_loggers])

# import julabo

# from asyncua.sync import Server as SyncServer, ua
# from .utility import set_ip, find_node_by_namespace_index, write_props, match_methods, binder

class Server:
    def __init__(self, devices:list[str]) -> None:
        self._log = logging.getLogger(__name__)
        self._server = asyncua.sync.Server()
        self._devices = devices
        # nodes shortcuts
        self.types:SyncNode = self._server.nodes.types
        self.objects:SyncNode = self._server.nodes.objects

    def set_endpoint(self, url):
        return self._server.set_endpoint(url=url)

    def import_xml_and_populate_devices(self, path):
        node_list:list[ua.NumericNodeId] = self._server.import_xml(path=path)
        object_type = self._filter_object_type(node_list=node_list)
        # all devices populated with same type
        self._populate(self._devices, object_type=object_type)
        return node_list

    # FIXME: wrong node id type?
    def _filter_object_type(self, node_list:list[ua.NumericNodeId]) -> SyncNode:
        idx, name = find_object_type(node_list, self._server)
        index = [
            "0:ObjectTypes",
            "0:BaseObjectType",
            f"{idx}:{name}"
            ]
        return self.types.get_child(index)

    def _populate(self, devices:list[str], object_type:SyncNode):
        q_name = object_type.read_browse_name()
        for device in devices:
            idx = self._server.register_namespace(device)
            deviceObject = self.objects.add_object(idx, q_name.Name, object_type)

            # bindings
            driver = Driver(device)
            for node, method in driver.bind(deviceObject):
                self._server.link_method(node, method)

    @property
    def opcua(self):
        return self._server

        # self.devices = []
        # self.idx = []
        # self._binded = {}

    #     self._silence_loggers()
    #     # default permissive manager + internal session
    #     self._server = SyncServer()
    #     # Narrov down security
    #     self._server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
    #     # public endpoint
    #     self._server.set_endpoint(f"opc.tcp://{set_ip(True)}:4840")

    # def __enter__(self):
    #     self.start()
    #     return self

    # def __exit__(self, exc_type, exc_value, traceback):
    #     self.stop()

    # def start(self):
    #     self._server.start()

    # def stop(self):
    #     if self._server.aio_obj.bserver:
    #         # if connected, stop connection
    #         self._server.stop()
    #     if self._server.tloop.is_alive():
    #         # if looping, stop the loop
    #         self._server.tloop.stop() 

    # def _silence_loggers(self):
    #     for _log in self._silence:
    #         logging.getLogger(_log).setLevel(logging.CRITICAL)

    # def _connect_driver(self, url):
    #     args = {
    #         "concurrency"       : "syncio",
    #         "auto_reconnect"    : True
    #     }
    #     device = julabo.JulaboCF(julabo.connection_for_url(url=url, **args))
    #     # not to be binded from device
    #     _excluded = ["__","write"]
    #     for name in dir(device):
    #         # is method
    #         if callable(bound := getattr(device, name)):
    #             # not containing forbiden characters
    #             if not any(x in name for x in _excluded):
    #                 self._binded[name] = bound

    # # def _populate_property(self, node, bindings):
    # #     pass

    # def populate(self, types_path, devices_path:list):
    #     self._server.import_xml(types_path)
    #     for path in devices_path:
    #         self._server.import_xml(path)

    #     all_namespaces = self._server.get_namespace_array()
    #     # TODO: implement better solution -> pop without popping
    #     last_namespace = all_namespaces[len(all_namespaces)-1]
    #     idx = self._server.get_namespace_index(last_namespace)
    #     device = find_node_by_namespace_index(idx, self)

    #     # FIXME: url from 'any' to 'urlBytes'{schema://hostname:port}
    #     self._connect_driver(last_namespace)
    #     # populate binder -> write props:all
    #     write_props(self._binded, device, self._log)
    #     for node, method in match_methods(device, self._binded):
    #         self._server.link_method(node, binder(method))
