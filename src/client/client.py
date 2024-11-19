import socket

def run_client(server_ip, server_port):
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the server
        client_socket.connect((server_ip, server_port))
        print(f"Connected to server at {server_ip}:{server_port}")
        
        while True:
            # Get user input from the terminal
            user_input = input("Enter message to send (type 'exit' to quit): ")
            
            if user_input.lower() == 'exit':
                print("Closing connection.")
                break
            
            if not user_input:
                print("Please enter a message.")
                continue
            # Send the input to the server
            client_socket.sendall(user_input.encode('utf-8'))
            
            # Optional: Receive and print server response
            response = client_socket.recv(1024)
            if not response:
                print("Server closed the connection.")
                client_socket.close()
                exit(0)
            print(f"Server response: {response.decode('utf-8')}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        print(f"\nKeyboard interrupt detected. Exiting...")
    finally:
        # Close the socket
        # client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()

# Change these as needed
SERVER_IP = "127.0.0.1"  # Replace with the server's IP address
SERVER_PORT = 65432      # Replace with the server's port number

if __name__ == "__main__":
    run_client(SERVER_IP, SERVER_PORT)
