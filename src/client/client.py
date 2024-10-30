import socket
import sys


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


def start_client(args):

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))  # Attempt to connect to the server
            print(f"Connected to server at {HOST}:{PORT}")
            while True:
                message = input("Enter message to send (or 'quit' to exit): ")
                if message.lower() == "quit":
                    break
                s.sendall(message.encode())
                data = s.recv(1024)
                print(f"Received from server: {data.decode()}")
    except socket.gaierror as e:
        print(f"Address-related error connecting to server: {e}")
    except socket.timeout as e:
        print(f"Connection timed out: {e}")
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    start_client(sys.argv)
