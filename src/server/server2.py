import socket
import threading
import logging
import signal
import sys
import time
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Server:
    def __init__(self, host='0.0.0.0', port=65432):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.shutdown_flag = False
        self.lock = threading.Lock()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
        except Exception as e:
            logging.error(f"Binding error: {e}")
            sys.exit(1)
        self.server_socket.listen(5)
        logging.info(f"Server listening on {self.host}:{self.port}")

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.accept_connections()

    def accept_connections(self):
        try:
            while not self.shutdown_flag:
                print("ici")
                time.sleep(1)
                client_socket, addr = self.server_socket.accept()
                logging.info(f"New connection from {addr}")
                with self.lock:
                    self.clients.append(client_socket)
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_thread.start()
        except OSError as e:
            if not self.shutdown_flag:
                logging.error(f"Server accept error: {e}")
        finally:
            self.server_socket.close()
            logging.info("Server socket closed")

    def handle_client(self, client_socket, addr):
        try:
            while not self.shutdown_flag:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode().strip()
                logging.info(f"Received from {addr}: {message}")
                response = f"Server received: {message}"
                client_socket.sendall(response.encode())
        except ConnectionResetError:
            logging.warning(f"Connection reset by {addr}")
        except (BrokenPipeError, OSError):
            logging.warning(f"Connection error with {addr}")
        except Exception as e:
            logging.error(f"Error with client {addr}: {e}")
        finally:
            self.cleanup_client(client_socket)
            logging.info(f"Connection closed with {addr}")

    def cleanup_client(self, client_socket):
        with self.lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
        try:
            client_socket.close()
        except Exception as e:
            pass

    def signal_handler(self, signum, frame):
        logging.info("Shutting down server gracefully...")
        self.shutdown_flag = True
        with self.lock:
            for client in self.clients:
                try:
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                except Exception as e:
                    pass
        try:
            self.server_socket.close()
        except Exception as e:
            pass
        sys.exit(0)

if __name__ == "__main__":
    server = Server()
    server.start()