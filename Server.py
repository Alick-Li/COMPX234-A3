import socket
import threading
import time

# The tuple_space dictionary stores all key-value pairs (tuples) managed by the server.
tuple_space = {}

# Variables to keep track of various statistics about server activity and tuple usage.
total_clients = 0         # Number of clients that have connected since the server started
total_operations = 0      # Total number of client operations handled (reads, gets, puts)
total_reads = 0           # Number of read operations
total_gets = 0            # Number of get (remove) operations
total_puts = 0            # Number of put (add) operations
total_errors = 0          # Number of error responses sent to clients

# Variables for tuple statistics, recalculated periodically in display_summary()
total_tuples = 0          # Total current tuples stored
average_tuple_size = 0    # Average size (characters) of each tuple (key + value)
average_key_size = 0      # Average size of keys
average_value_size = 0    # Average size of values

def handle_client(client_socket, client_address):
    """
    Handles communication with a single client.
    Receives commands, processes them, updates statistics, and sends replies.
    Runs in its own thread for each client connection.
    """
    global total_clients
    global total_operations
    global total_reads
    global total_gets
    global total_puts
    global total_errors

    total_clients += 1  # Increment total client counter

    try:
        while True:
            # Receive a request message from the client (max 1024 bytes)
            request_message = client_socket.recv(1024).decode('utf-8')
            # Split the message into parts: [size, command, key, (optional) value]
            parts = request_message.split(' ')
            size = parts[0]      # The reported message size (not used for validation here)
            command = parts[1]   # Command letter: 'R', 'G', or 'P'
            key = parts[2]       # The tuple key to operate on
            if command == 'P':
                value = parts[3] # The value for put/add operations
            else:
                value = None     # No value needed for read/get

            # Process a READ command: check if key exists, return value or error
            if command == 'R':
                total_operations += 1
                total_reads += 1
                if key in tuple_space:
                    value = tuple_space[key]
                    # Compose a successful read response, including tuple data
                    response_message = f"{(16 + len(key) + len(value)):03d} OK ({key}, {value}) read"
                else:
                    total_errors += 1
                    # Key not found; send error response
                    response_message = f"{(23 + len(key)):03d} ERR {key} does not exist"

            # Process a GET command: check if key exists, remove and return value or error
            elif command == 'G':
                total_operations += 1
                total_gets += 1
                if key in tuple_space:
                    value = tuple_space[key]
                    del tuple_space[key]  # Remove the tuple from storage
                    # Compose a successful remove response, including tuple data
                    response_message = f"{(19 + len(key) + len(value)):03d} OK ({key}, {value}) removed"
                else:
                    total_errors += 1
                    # Key not found; send error response
                    response_message = f"{(23 + len(key)):03d} ERR {key} does not exist"

            # Process a PUT command: check if key already exists, add or send error
            elif command == 'P':
                total_operations += 1
                total_puts += 1
                if key in tuple_space:
                    total_errors += 1
                    # Key already exists; send error response
                    response_message = f"{(23 + len(key) + len(value)):03d} ERR {key} already exists"
                else:
                    tuple_space[key] = value  # Store the new tuple
                    # Compose a successful add response
                    response_message = f"{(13 + len(key)):03d} OK {key} added"

            # Send the response message back to the client
            client_socket.sendall(response_message.encode('utf-8'))

    except Exception as e:
        # Print any error that occurs while handling this client
        print(f'Error in handling client {client_address}: {e}')
    finally:
        # Ensure the client socket is always closed when finished
        client_socket.close()
        print(f'Connection with {client_address} has been closed.')

def display_summary():
    """
    Runs in a background thread to compute and print statistics about tuple space
    and server usage every 10 seconds. Helps with monitoring the server state.
    """
    global total_tuples
    global average_tuple_size
    global average_key_size
    global average_value_size

    while True:
        total_tuples = len(tuple_space)  # Update the current number of tuples
        if total_tuples > 0:
            # Calculate averages over all tuples for monitoring
            average_tuple_size = sum(len(key) + len(value) for key, value in tuple_space.items()) / total_tuples
            average_key_size = sum(len(key) for key in tuple_space.keys()) / total_tuples
            average_value_size = sum(len(value) for value in tuple_space.values()) / total_tuples
        else:
            # No tuples present; all averages are zero
            average_tuple_size = 0
            average_key_size = 0
            average_value_size = 0

        # Print a formatted summary to the console
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
        # Wait 10 seconds before next summary
        time.sleep(10)

def start_server(hostname, port_number):
    """
    Main entry point for starting the server.
    Sets up the TCP socket, listens for clients, and launches a new thread for each client.
    Also starts the summary display thread.
    """
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (hostname, port_number)
    # Bind the socket to the specified hostname and port
    server_socket.bind(server_address)
    # Start listening for incoming connections (max 5 queued clients)
    server_socket.listen(5)
    print('Server is running and ready to accept multiple clients...')

    # Start the thread that displays tuple space and server statistics
    threading.Thread(target=display_summary).start()

    try:
        # Main loop: accept and handle clients indefinitely
        while True:
            # Accept a new client connection (blocking call)
            client_socket, client_address = server_socket.accept()
            # Start a new thread to handle this client independently
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        # Gracefully handle CTRL+C to shut down the server
        print('Shutting down the server...')
    finally:
        # Close the server socket when done
        server_socket.close()

if __name__ == "__main__":
    # If this script is run directly, start the server on localhost and port 51234
    start_server('localhost', 51234)
