import readline, socket, sys

def start_client(server_ip: str, server_port: int):

    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((server_ip, server_port))
        # print(f"Connected to server at {server_ip}:{server_port}")

        while True:
            # Get user input from the terminal
            user_input = input("taskmaster> (type 'help'): ")

            if not user_input:
                continue

            readline.add_history(user_input)
            user_input = user_input[:1024]
            if user_input == "exit":
                print("Closing connection.")
                break
            else:
                # Send the input to the server
                client_socket.sendall(user_input.encode("utf-8"))

                # Optional: Receive and print server response
                response = client_socket.recv(1024)
                if not response:
                    print("Server closed the connection. Exiting")
                    client_socket.close()
                    exit(0)
                print(f"{response.decode('utf-8')}")

    except Exception as e:
        print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        pass
        # print(f"\nKeyboard interrupt detected. Exiting")
    finally:
        # Close the socket
        # client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:", sys.argv[0], "<host> <port>")
        sys.exit(1)
    SERVER_IP: str = sys.argv[1]
    SERVER_PORT: int = int(sys.argv[2])
    start_client(SERVER_IP, SERVER_PORT)