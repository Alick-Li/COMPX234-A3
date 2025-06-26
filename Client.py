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

# Dictionary used as the tuple space to store key-value pairs
tuple_space = {}

# Statistics for monitoring server operations
total_clients = 0      # Total number of clients connected
total_operations = 0   # Total number of operations executed
total_reads = 0        # Total number of READ operations
total_gets = 0         # Total number of GET operations
total_puts = 0         # Total number of PUT operations
total_errors = 0       # Total number of errors occurred

# Statistics for tuple space analysis
total_tuples = 0           # Current number of tuples in the tuple space
average_tuple_size = 0     # Average size of each tuple (key + value)
average_key_size = 0       # Average size of keys
average_value_size = 0     # Average size of values

def handle_client(client_socket, client_address):
    """
    Handles communication with a single client:
    Processes requests, updates statistics, and sends responses.
    """
    global total_clients
    global total_operations
    global total_reads
    global total_gets
    global total_puts
    global total_errors

    total_clients += 1  # A new client has connected

    try:
        while True:
            # Receive and decode the client's request message
            request_message = client_socket.recv(1024).decode('utf-8')
            parts = request_message.split(' ')
            size = parts[0]      # Message size (not used)
            command = parts[1]   # Operation code: R (READ), G (GET), or P (PUT)
            key = parts[2]       # Key for the operation
            if command == 'P':
                value = parts[3] # Value for PUT command
            else:
                value = None     # Other operations do not have a value

            # Handle READ operation (read without removal)
            if command == 'R':
                total_operations += 1
                total_reads += 1
                if key in tuple_space:
                    value = tuple_space[key]
                    # Construct a success response message
                    response_message = f"{(16 + len(key) + len(value)):03d} OK ({key}, {value}) read"
                else:
                    total_errors += 1
                    # Construct an error response message
                    response_message = f"{(23 + len(key)):03d} ERR {key} does not exist"

            # Handle GET operation (read and remove)
            elif command == 'G':
                total_operations += 1
                total_gets += 1
                if key in tuple_space:
                    value = tuple_space[key]
                    del tuple_space[key]  # Remove key-value pair after GET
                    response_message = f"{(19 + len(key) + len(value)):03d} OK ({key}, {value}) removed"
                else:
                    total_errors += 1
                    response_message = f"{(23 + len(key)):03d} ERR {key} does not exist"

            # Handle PUT operation (add a new key-value pair)
            elif command == 'P':
                total_operations += 1
                total_puts += 1
                if key in tuple_space:
                    total_errors += 1
                    # If the key already exists, return an error
                    response_message = f"{(23 + len(key) + len(value)):03d} ERR {key} already exists"
                else:
                    tuple_space[key] = value  # Add the new key-value pair
                    response_message = f"{(13 + len(key)):03d} OK {key} added"

            # Send the response message back to the client
            client_socket.sendall(response_message.encode('utf-8'))

    except Exception as e:
        print(f'Error in handling client {client_address}: {e}')
    finally:
        client_socket.close()  # Close the connection with the client
        print(f'Connection with {client_address} has been closed.')

def display_summary():
    """
    Periodically prints the status and statistics of the server and tuple space.
    """
    global total_tuples
    global average_tuple_size
    global average_key_size
    global average_value_size

    while True:
        total_tuples = len(tuple_space)  # Current number of key-value pairs
        if total_tuples > 0:
            # Calculate average tuple size, key size, and value size
            average_tuple_size = sum(len(key) + len(value) for key, value in tuple_space.items()) / total_tuples
            average_key_size = sum(len(key) for key in tuple_space.keys()) / total_tuples
            average_value_size = sum(len(value) for value in tuple_space.values()) / total_tuples
        else:
            average_tuple_size = 0
            average_key_size = 0
            average_value_size = 0

        # Print statistics summary
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
        time.sleep(10)  # Update statistics every 10 seconds

def start_server(hostname, port_number):
    """
    Initializes and starts the server to listen for client connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (hostname, port_number)
    server_socket.bind(server_address)
    server_socket.listen(5)
    print('Server is running and ready to accept multiple clients...')

    # Start the summary display in a separate thread
    threading.Thread(target=display_summary).start()

    try:
        while True:
            # Accept a new client connection
            client_socket, client_address = server_socket.accept()
            # Start a new thread to handle this client
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        print('Shutting down the server...')
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server('localhost', 51234)  # Start the server and listen on localhost:51234
