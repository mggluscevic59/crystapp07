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