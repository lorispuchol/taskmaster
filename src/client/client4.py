import socket
import logging
import sys
import readline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_client(host='127.0.0.1', port=65432):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        logging.info("Connected to server")

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
                    logging.info("Server closed the connection")
                    break
                print(f"Received from server: {data.decode()}")
            except (ConnectionResetError, BrokenPipeError):
                logging.error("Connection lost with server")
                break
            except Exception as e:
                logging.error(f"Communication error: {e}")
                break

    except ConnectionRefusedError:
        logging.error("Server is not running")
    except KeyboardInterrupt:
        logging.info("Client shutdown by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if sock:
            sock.close()
        logging.info("Disconnected from server")

if __name__ == "__main__":
    run_client()