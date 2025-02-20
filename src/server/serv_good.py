import socket
import selectors
import sys
import signal
from utils.logger import logger

sel = selectors.DefaultSelector()
shutdown_flag = False

def signal_handler(sig, frame):
    global shutdown_flag
    logger.info("Shutting down server...")
    shutdown_flag = True
    sel.close()
    sys.exit(0)

def accept_connection(sock):
    conn, addr = sock.accept()
    logger.info(f"Accepted connection from {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=handle_client)

def handle_client(conn):
    addr = conn.getpeername()
    try:
        data = conn.recv(1024)
        if data:
            message = data.decode().strip()
            logger.info(f"Received from {addr}: {message}")
            # message = execute_command_here
            response = f"Server receivedtest: {message}"
            conn.sendall(response.encode())
        else:
            logger.info(f"Connection closed by {addr}")
            sel.unregister(conn)
            conn.close()
    except ConnectionResetError:
        logger.warning(f"Connection reset by {addr}")
        sel.unregister(conn)
        conn.close()
    except Exception as e:
        logger.error(f"Error with {addr}: {e}")
        sel.unregister(conn)
        conn.close()

import time

def run_server(host='0.0.0.0', port=65432):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_sock.bind((host, port))
        server_sock.listen()
        server_sock.setblocking(False)
        sel.register(server_sock, selectors.EVENT_READ, data=accept_connection)
        logger.info(f"Server listening on {host}:{port}")

        while not shutdown_flag:
            print("ici")
            events = sel.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
            if not events:
                # process_monitoring()
                pass
                
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Cleaning up server...")
        server_sock.close()
        sel.close()

if __name__ == "__main__":
    run_server()