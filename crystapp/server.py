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

class Server:
    def __init__(self, devices:list[str]) -> None:
        self._log = logging.getLogger(__name__)
        self._server = asyncua.sync.Server()
        self._devices = devices
        # nodes shortcuts
        self.types:SyncNode = self._server.nodes.types
        self.objects:SyncNode = self._server.nodes.objects
        
        # silences some alerts
        self._server.set_security_policy([ua.SecurityPolicyType.NoSecurity])

    def set_endpoint(self, url):
        return self._server.set_endpoint(url=url)

    def get_namespace_index(self, url:str):
        return self._server.get_namespace_index(url)

    def import_xml_and_populate_devices(self, path):
        node_list:list[ua.NumericNodeId] = self._server.import_xml(path=path)
        object_type = self._filter_object_type(node_list=node_list)
        # all devices populated with same type
        self._populate(self._devices, object_type=object_type)
        return node_list

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
