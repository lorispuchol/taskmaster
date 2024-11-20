import selectors
import socket
import types
import sys

sel = selectors.DefaultSelector()


def parse_request(request) -> bool:
    return 0


def perform_request(request) -> bytes:
    str = b""
    str += b"response="
    str += request
    return str


def accept_wrapper(sock):
    # since listening socket was registered for the event selectors.EVENT_READ, it should be
    # ready to read
    # Hence we can call sock.accept()
    conn, addr = sock.accept()
    print("Accepted connection from", addr)

    # we set socket in non-blocking mode again
    conn.setblocking(False)

    # creates an object to hold the data we want included along with the socket
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")

    # monitors to check when the client connection is ready for reading and writing
    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    # the arguments are socket, mask, and data
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    # key is the 'namedtuple' returned from select() that contains
    # - sockobject: fileobj
    # - data object - data
    sock = key.fileobj
    data = key.data

    # 'mask' contains the events taht are ready
    try:
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # should be ready to read
            print("Received", repr(recv_data), "from", data.addr)
            if recv_data:
                if recv_data == b"shutdown":
                    raise Exception("Shutdown command received")
                parse_request(recv_data)
                data.outb += perform_request(recv_data)
                # any data that's read is appended to data.outb so it can be sent later
            # block if no data is received
            # this means that the client has closed their socket
            else:
                print("Closing connection to", data.addr)

                # unregister so that it's no longer monitered by select()
                sel.unregister(sock)

                # close the socket
                sock.close()

        # a healthy socket should always be ready for writing
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print("Echoing", repr(data.outb), "to", data.addr)

                # any received data stored in data.outb is echoed to the client
                sent = sock.send(data.outb)  # should be ready to write

                # the bytes sent are then removed from the buffer
                data.outb = data.outb[sent:]
    except ConnectionResetError:
        print(f"Connection was reset by peer: {data.addr}")
        sel.unregister(sock)
        sock.close()
    except Exception as e:
        raise e


def start_server(host: str, port: int):
    print("Starting server...")
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    print(f"Server listening on {host}:{port}")

    # this is different from 'echo-server.py' as lsock is set to non-blocking mode
    # when it's used with sel.select() below, we can wait for events on one or more sockets
    # and read and write data when it's ready
    # - key: a SelectorKey 'namedtuple' that contains a 'fileobj' attribute
    # - mask: an event mask of the operations that are ready
    lsock.setblocking(False)

    # this registers the socket to be monitored with sel.select() for the events we are
    # interested in
    # data - is used to store whatever arbitrary data we'd like along with the socket.
    # It's returned when select() returns. data will be used to keep track what's been sent
    # and received on the socket.
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:

            # sel.select(timeout=None) blocks until there are sockets ready for I/O.
            # It returns a list of (key, event) tuples, one for each socket.
            events = sel.select(timeout=None)
            for key, mask in events:
                # if key.data 'None', we know it's from the listening socket and we need to accept()
                # the connection
                if key.data is None:
                    accept_wrapper(key.fileobj)
                # if key.data is not 'None', we know it's a client that's already been accepted, and
                # we need to service it.
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt, Exiting")
        lsock.shutdown(socket.SHUT_RDWR)
        lsock.close()
    except Exception as e:
        print(f"{e}")
        print(f"Exiting")
    finally:
        sel.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:", sys.argv[0], "<host> <port>")
        sys.exit(1)
    HOST: str = sys.argv[1]
    PORT: int = int(sys.argv[2])
    start_server(HOST, PORT)
