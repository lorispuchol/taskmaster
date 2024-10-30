import selectors
import socket
import sys

HOST = "127.0.0.1"
PORT = 65432


def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Connected by {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=addr)


def service_connection(key, mask):
    sock = key.fileobj
    addr = key.data
    if mask & selectors.EVENT_READ:
        data = sock.recv(1024)
        if data.strip() == "":  # Check if only Enter is pressed or message is empty/whitespace
            print(f"Empty message received from {addr}")
            sock.sendall("Empty message received. Please send something meaningful.\n".encode())
        elif data:
            print(f"Received: {data.decode()} from {addr}")
            sock.sendall(f"Server received: {data.decode()}".encode())
        else:
            print(f"Closing connection to {addr}")
            sel.unregister(sock)
            sock.close()


sel = selectors.DefaultSelector()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        s.setblocking(False)
        sel.register(s, selectors.EVENT_READ, data=None)
        print(f"Server listening on {HOST}:{PORT}")

        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)
        except KeyboardInterrupt:
            print("\nExiting taskmaster")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            sel.close()
            s.close()
            print("Server closed")


if __name__ == "__main__":
    start_server()
