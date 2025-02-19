import socket
import threading
import signal

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.skt = None
    
    def start_server(self):
        try:
            self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.skt.bind((self.host, self.port))
            self.skt.listen()
            print(f"Server started on {self.host}:{self.port}")
            self.start_accepting()
        except Exception as e:
            print(f"Error starting server: {e}")
            if self.skt is not None:
                self.skt.close()
    
    def start_accepting(self):
        while True:
            try:
                conn, addr = self.skt.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn,))
                client_thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                break
    
    def handle_client(self, conn):
        try:
            if not conn:
                return
            conn.sendall(b"Hello from the server!\r\n")
            data = conn.recv(1024).decode()
            if not data:
                print("Client disconnected unexpectedly")
                return
            conn.sendall(b"Received: " + data)
            conn.close()
        except Exception as e:
            print(f"Error handling client: {e}")
            if conn is not None:
                conn.close()

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.skt = None
    
    def connect_to_server(self):
        try:
            self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.skt.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
            self.send_data()
        except Exception as e:
            print(f"Connection error: {e}")
            if self.skt is not None:
                self.skt.close()
    
    def send_data(self):
        try:
            msg = "Hello from the client\r\n"
            self.skt.sendall(msg.encode())
            response = self.skt.recv(1024)
            if not response:
                print("Connection closed by server")
            else:
                print("Server responded: " + response.decode())
            self.close_connection()
        except Exception as e:
            print(f"Error sending data: {e}")
            self.close_connection()
    
    def close_connection(self):
        try:
            if self.skt is not None:
                self.skt.close()
                self.skt = None
        except Exception as e:
            pass

def main():
    import sys
    args = sys.argv
    if len(args) < 3:
        print("Usage: python server.py <host> <port>")
        return
    
    host, port = args[1], int(args[2])
    
    signal.signal(signal.SIGINT, lambda s, i: sys.exit(0))
    
    try:
        server = Server(host, port)
        print("Starting server...")
        server.start_server()
    except Exception as e:
        print(f"Main error: {e}")

if __name__ == "__main__":
    main()
