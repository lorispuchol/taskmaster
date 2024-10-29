import socket
from shared.global_variables import programs, config


def start_server():
    try:
        host = "127.0.0.1"  # localhost
        port = 65432  # Port to listen on (non-privileged ports are > 1023)

        # AF_INET is the address family for IPv4
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Bind the socket to the address and port
            s.bind((host, port))
            # Enable the server to accept connections
            s.listen()
            print(f"Server listening on {host}:{port}")

            while True:
                # Accept a connection from a client
                # conn is a new socket object usable to send and receive data on the connection
                # addr is the address bound to the socket on the other end of the connection.
                (conn, addr) = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        print(f"Received: {data.decode()}")
                        conn.sendall(f"Server received: {data.decode()}".encode())
    except Exception as e:
        print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        print("\nExiting taskmaster")
    finally:
        s.close()
        print("Server closed")


if __name__ == "__main__":
    start_server()
