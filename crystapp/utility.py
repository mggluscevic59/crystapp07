import logging
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM

# devices configurtion
cfg = {
    "devices": [{
        "name": "jul-1",
        "class": "JulaboCF",
        "transports": [
            {"type": "tcp", "url": "localhost:5050"}
        ]
    }]
}

# hostname, port
def extract_socket_data(server):
    address:tuple = ("", 0)
    ports:list[address] = []
    for device in server.devices.values():
        for transport in device.transports:
            ports.append(transport.address)
    return ports

def broadcast(hostname, port):
    from julabo import connection_for_url, JulaboCF
    test_2 = connection_for_url(
        f"tcp://{hostname}:{port}",
        concurrency = "syncio"  
    )
    test_2.open()
    test_3 = JulaboCF(test_2)
    result = test_3.status()
    print(result)

def set_ip(is_public):
    if not is_public:
        return "localhost"
    return get_ip()

def get_ip():
    """ https://stackoverflow.com/a/28950776/2475919 """
    _log = logging.getLogger(__name__)
    with socket(AF_INET, SOCK_DGRAM) as searcher:
        searcher.settimeout(0)
        try:
            # doesn't even have to be reachable
            searcher.connect(('10.254.254.254', 1))
            ip = searcher.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
            _log.info("Defaulting to localhost!")
        finally:
            searcher.close()
        return ip
