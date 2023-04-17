import logging
# import sys
import asyncua.ua.uaerrors

from asyncua import uamethod
from asyncua.sync import SyncNode, ua
from julabo import connection_for_url, JulaboCF

class Driver:
    def __init__(self, url) -> None:
        self._log = logging.getLogger(__name__)
        self._log.info("Initializing device driver")
        self.methods:list[callable] = {}

        # arguments => thread encapsulated asyncio, no connection open needed
        args = {
                    "concurrency"       : "syncio",
                    "auto_reconnect"    : True
                }
        self._device = JulaboCF(connection_for_url(url=url, **args))

        # not to be binded from device
        _excluded = ["__","write"]
        for name in dir(self._device):
            # is method
            if callable(bound := getattr(self._device, name)):
                # not containing forbiden characters
                if not any(x in name for x in _excluded):
                    self.methods[name] = bound

    def bind(self, parent:SyncNode):
        def binder(bound):
            @uamethod
            def _method(parent:ua.NodeId, *argv):
                try:
                    if argv:
                        try:
                            input, *_ = argv
                            return bound(input)
                        except TypeError:
                            nice_name = f"ns={parent.NamespaceIndex};i={parent.Identifier}"
                            mssg = f"Node {nice_name} takes 1 positional argument but 2 were given"
                            self._log.info(mssg)
                    else:
                        return bound()
                except ConnectionRefusedError:
                    nice_name = f"ns={parent.NamespaceIndex};i={parent.Identifier}"
                    mssg = f"Node {nice_name} not available"
                    self._log.info(mssg)
                    return asyncua.ua.uaerrors.BadCommunicationError()
            return _method
        methods_only = {
            "refs":ua.ObjectIds.HasComponent,
            "nodeclassmask":ua.NodeClass.Method
        }
        children:list[SyncNode] = parent.get_children(**methods_only)
        for child in children:
            q_name = child.read_browse_name()
            method = self.methods[str(q_name.Name).lower()]
            yield child, binder(method)
