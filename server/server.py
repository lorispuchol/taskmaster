import socket


def start_server():
    host = "127.0.0.1"  # localhost
    port = 65432  # Port to listen on (non-privileged ports are > 1023)

    # AF_INET is the address family for IPv4
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f"Received: {data.decode()}")
                    conn.sendall(f"Server received: {data.decode()}".encode())
        s.close()


if __name__ == "__main__":
    start_server()
