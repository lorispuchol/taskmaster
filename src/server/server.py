import socket
import sys
import yaml


def parse_config(config_file) -> dict:
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_file}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    else:
        print("Config file parsed successfully")
        return config


def start_server():
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


def check_config(config: dict) -> bool:

    required_fields = ["programs"]

    if not config:
        print("ERROR: Config file\nConfig file is empty")
        return False

    if not isinstance(config, dict):
        print("ERROR: Config file\nConfig file must start by an object")
        return False

    for field in required_fields:
        if field not in config:
            print(f"ERROR: Config file\nConfig file is missing required field: {field}")
            return False

    if not isinstance(config["programs"], dict):
        print("ERROR: Config file\n'programs' field must be one or more objects")
        return False

    return True


def taskmaster():
    config: dict = parse_config(sys.argv[1])
    print(config)
    if check_config(config):
        # start_server()
        pass
    else:
        print("Config file is invalid")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <config_file>")
        sys.exit(1)
    taskmaster()
