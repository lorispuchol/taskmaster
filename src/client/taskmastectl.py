import socket, readline
from cmd import is_valid_cmd, print_short_help, print_large_help

def run_client(host='127.0.0.1', port=65432):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        while True:
            message = input("taskmasterctl> (try 'help'): ")
            if not message:
                continue
            message = message[:4096]
            if is_valid_cmd(message) is False:
                print_short_help()
                continue
            if (message.split()[0] == "help"):
                print_large_help()
                continue
            readline.add_history(message)
            if message.split()[0] == 'exit':
                break
            try:
                sock.sendall(message.encode())
                data = sock.recv(4096)
                if not data:
                    print("Server closed the connection, you are disconnected")
                    break
                print(f"{data.decode()}")
            except (ConnectionResetError, BrokenPipeError):
                print("Connection lost with server")
                break
            except Exception as e:
                print(f"Communication error: {e}")
                break

    except ConnectionRefusedError:
        print("Server is not running")
    except KeyboardInterrupt:
        print("Client shutdown by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if sock:
            sock.close()
        print("Interactive controller exited")

if __name__ == "__main__":
    run_client()