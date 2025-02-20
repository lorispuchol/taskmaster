import socket
import readline
from utils.logger import logger

def run_client(host='127.0.0.1', port=65432):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        logger.info("Connected to server")

        while True:
            message = input("Enter message (type 'exit' to quit): ")
            if not message:
                continue
            message = message[:1024]
            readline.add_history(message)
            if message.lower() == 'exit':
                break
            try:
                sock.sendall(message.encode())
                data = sock.recv(1024)
                if not data:
                    logger.info("Server closed the connection")
                    break
                print(f"Received from server: {data.decode()}")
            except (ConnectionResetError, BrokenPipeError):
                logger.error("Connection lost with server")
                break
            except Exception as e:
                logger.error(f"Communication error: {e}")
                break

    except ConnectionRefusedError:
        logger.error("Server is not running")
    except KeyboardInterrupt:
        logger.info("Client shutdown by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if sock:
            sock.close()
        logger.info("Disconnected from server")

if __name__ == "__main__":
    run_client()