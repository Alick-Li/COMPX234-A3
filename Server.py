import socket
import threading
import time

# Global dictionary to store key-value pairs (tuple space)
tuple_space = {}

# Global statistics counters
total_clients = 0       # Total number of clients connected
total_operations = 0    # Total number of operations performed
total_reads = 0         # Total number of READ operations
total_gets = 0          # Total number of GET operations
total_puts = 0          # Total number of PUT operations
total_errors = 0        # Total number of error responses

# Global statistics for tuple space analysis
total_tuples = 0        # Current number of tuples in space
average_tuple_size = 0  # Average size of tuples (key + value)
average_key_size = 0    # Average size of keys
average_value_size = 0  # Average size of values

def handle_client(client_socket, client_address):
    """
    Handle individual client connections and process their requests.
    
    Args:
        client_socket: Socket object for client communication
        client_address: Client's address information
    """
    # Access global statistics variables
    global total_clients
    global total_operations
    global total_reads
    global total_gets
    global total_puts
    global total_errors

    # Increment client counter
    total_clients += 1

    try:
        # Continuously listen for client requests
        while True:
            # Receive and decode request message from client
            request_message = client_socket.recv(1024).decode('utf-8')
            
            # Parse the request message
            # Format: [size] [command] [key] [value (for PUT only)]
            parts = request_message.split(' ')
            size = parts[0]     # Message size (not used in processing)
            command = parts[1]  # Command type: R (READ), G (GET), P (PUT)
            key = parts[2]      # Key for the operation
            
            # Extract value for PUT command, None for others
            if command == 'P':
                value = parts[3]
            else:
                value = None

            # Process READ command
            if command == 'R':
                total_operations += 1
                total_reads += 1
                
                # Check if key exists in tuple space
                if key in tuple_space:
                    # Key found: return the value
                    value = tuple_space[key]
                    response_message = f"{(16 + len(key) + len(value)):03d} OK ({key}, {value}) read"
                else:
                    # Key not found: return error
                    total_errors += 1
                    response_message = f"{(23 + len(key)):03d} ERR {key} does not exist"
                    
            # Process GET command (read and remove)
            elif command == 'G':
                total_operations += 1
                total_gets += 1
                
                # Check if key exists in tuple space
                if key in tuple_space:
                    # Key found: get value and remove from tuple space
                    value = tuple_space[key]
                    del tuple_space[key]
                    response_message = f"{(19 + len(key) + len(value)):03d} OK ({key}, {value}) removed"
                else:
                    # Key not found: return error
                    total_errors += 1
                    response_message = f"{(23 + len(key)):03d} ERR {key} does not exist"
                    
            # Process PUT command (add new key-value pair)
            elif command == 'P':
                total_operations += 1
                total_puts += 1
                
                # Check if key already exists
                if key in tuple_space:
                    # Key already exists: return error
                    total_errors += 1
                    response_message = f"{(23 + len(key) + len(value)):03d} ERR {key} already exists"
                else:
                    # Key doesn't exist: add new tuple to space
                    tuple_space[key] = value
                    response_message = f"{(13 + len(key)):03d} OK {key} added"

            # Send response back to client
            client_socket.sendall(response_message.encode('utf-8'))

    except Exception as e:
        # Handle any errors during client communication
        print(f'Error in handling client {client_address}: {e}')
    finally:
        # Ensure client socket is properly closed
        client_socket.close()
        print(f'Connection with {client_address} has been closed.')

def display_summary():
    """
    Continuously display server statistics and tuple space information.
    This function runs in a separate thread and updates every 10 seconds.
    """
    global total_tuples
    global average_tuple_size
    global average_key_size
    global average_value_size

    while True:
        # Calculate current statistics
        total_tuples = len(tuple_space)
        
        # Calculate averages only if tuples exist
        if total_tuples > 0:
            # Average total size (key + value) of all tuples
            average_tuple_size = sum(len(key) + len(value) for key, value in tuple_space.items()) / total_tuples
            # Average key size across all tuples
            average_key_size = sum(len(key) for key in tuple_space.keys()) / total_tuples
            # Average value size across all tuples
            average_value_size = sum(len(value) for value in tuple_space.values()) / total_tuples
        else:
            # No tuples exist: set all averages to 0
            average_tuple_size = 0
            average_key_size = 0
            average_value_size = 0

        # Display formatted statistics summary
        print(f'______________________________')
        print(f'Total Tuples       |{total_tuples}')
        print(f'Average Tuple Size |{average_tuple_size}')
        print(f'Average Key Size   |{average_key_size}')
        print(f'Average Value Size |{average_value_size}')
        print(f'Total Clients      |{total_clients}')
        print(f'Total Operations   |{total_operations}')
        print(f'Total READs        |{total_reads}')
        print(f'Total GETs         |{total_gets}')
        print(f'Total PUTs         |{total_puts}')
        print(f'Total Errors       |{total_errors}')
        
        # Wait 10 seconds before next update
        time.sleep(10)

def start_server(hostname, port_number):
    """
    Initialize and start the server to accept client connections.
    
    Args:
        hostname (str): Server hostname or IP address
        port_number (int): Port number to listen on
    """
    # Create TCP socket for server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (hostname, port_number)
    
    # Bind socket to address and start listening
    server_socket.bind(server_address)
    server_socket.listen(5)  # Allow up to 5 pending connections
    print('Server is running and ready to accept multiple clients...')

    # Start statistics display thread
    threading.Thread(target=display_summary).start()

    try:
        # Main server loop: accept and handle client connections
        while True:
            # Accept new client connection
            client_socket, client_address = server_socket.accept()
            # Create new thread to handle this client
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        print('Shutting down the server...')
    finally:
        # Ensure server socket is properly closed
        server_socket.close()

if __name__ == "__main__":
    # Start server on localhost port 51234
    start_server('localhost', 51234)