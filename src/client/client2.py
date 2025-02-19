import socket
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_client(host='127.0.0.1', port=65432):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        logging.info("Connected to server")
        
        while True:
            message = input("Enter message (type 'exit' to quit): ")
            if message.lower() == 'exit':
                break
            
            try:
                client_socket.sendall(message.encode())
                data = client_socket.recv(1024)
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
        try:
            client_socket.close()
        except Exception as e:
            pass
        logging.info("Disconnected from server")

if __name__ == "__main__":
    run_client()