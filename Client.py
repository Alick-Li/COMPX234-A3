import socket
import threading
import time

def client_task(hostname, port_number, pathname):
    """
    Execute client task to send requests to server from a request file.
    
    Args:
        hostname (str): Server hostname or IP address
        port_number (int): Server port number
        pathname (str): Path to the request file containing commands
    """
    try:
        # Create a TCP socket for client connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (hostname, port_number)
        # Connect to the server
        client_socket.connect(server_address)

        # Read and process each line from the request file
        with open(pathname, 'r') as file:
            for line in file:
                # Parse command line: split by space to get command, key, and value
                parts = line.strip().split(' ')
                command = parts[0]  # First part is the command (READ, GET, PUT)
                key = parts[1]      # Second part is the key
                # For PUT command, join remaining parts as value; otherwise None
                value = ' '.join(parts[2:]) if command == 'PUT' else None

                # Validate message size constraints (max 970 characters)
                if command in ['READ', 'GET']:
                    if len(key) > 970:
                        print('Error: Key size exceeds 970 characters')
                        continue
                elif command == 'PUT':
                    # Check combined key and value size for PUT command
                    if len(key + ' ' + value) > 970:
                        print('Error: Collated size exceeds 970 characters')
                        continue

                # Format request message according to protocol:
                # Format: [3-digit length][space][command][space][key][space][value]
                if command == 'READ':
                    # READ command: length + "R" + key
                    request_message = f"{(6 + len(key)):03d} R {key}"
                elif command == 'GET':
                    # GET command: length + "G" + key
                    request_message = f"{(6 + len(key)):03d} G {key}"
                elif command == 'PUT':
                    # PUT command: length + "P" + key + value
                    request_message = f"{(7 + len(key) + len(value)):03d} P {key} {value}"

                # Send the formatted request to server
                client_socket.sendall(request_message.encode('utf-8'))

                # Receive and decode server response
                response_message = client_socket.recv(1024).decode('utf-8')
                # Print response with client identifier (extracted from filename)
                print(f'{pathname[14:22]} received: {response_message}')

    except Exception as e:
        # Handle any connection or file operation errors
        print(f"Error for {pathname[14:22]}: {e}")
    finally:
        # Ensure socket is properly closed
        client_socket.close()

def main():
    """
    Main function to create and manage multiple client threads.
    Creates 10 concurrent clients, each processing a different request file.
    """
    clients = []  # List to store client thread objects

    # Create and start 10 client threads
    for i in range(1, 11):
        # Create a new thread for each client with unique request file
        t = threading.Thread(target=client_task, args=('localhost', 51234, f'Request Files\\client_{i}.txt'))
        clients.append(t)
        t.start()  # Start the thread
        time.sleep(0.1)  # Small delay between thread starts to avoid overwhelming server

    # Wait for all client threads to complete
    for t in clients:
        t.join()

if __name__ == "__main__":
    main()