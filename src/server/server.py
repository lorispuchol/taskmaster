# multiconn-server.py

import sys
import socket
import selectors
import types
import subprocess


sel = selectors.DefaultSelector()

host = "127.0.0.1"
port = 65432

# multiconn-server.py

# ...

clients = []

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    global clients
    clients.append((conn, sock))
    print(f"clis: {(clients)}")


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


def kill_clients():

    global port

    try:
        # Get the process ID(s) using lsof
        result = subprocess.check_output(["lsof", "-ti", f"tcp:{port}"])
        pids = result.decode().strip().split('\n')

        # Kill each process ID
        for pid in pids:
            subprocess.run(["kill", pid])
            print(f"Killed process {pid} on port {port}")

    except subprocess.CalledProcessError:
        print(f"No process is running on port {port}")

def start_server():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print(f"Listening on {(host, port)}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    # multiconn-server.py

    # ...

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt, exiting")

    finally:
        global clients
        for client in clients:
            print(f"Closing connection to {client}")
            sel.unregister(client[1])
            client[1].shutdown(socket.SHUT_RDWR)
            (client[1]).close()
            # kill_clients()
        sel.close()
        lsock.close()
