import socket
import threading
import time

tuple_space = {}

total_clients = 0
total_operations = 0
total_reads = 0
total_gets = 0
total_puts = 0
total_errors = 0

total_tuples = 0
average_tuple_size = 0
average_key_size = 0
average_value_size = 0

def handle_client(client_socket, client_address):
    global total_clients
    global total_operations
    global total_reads
    global total_gets
    global total_puts
    global total_errors

    total_clients += 1

    try:
        while True:
            request_message = client_socket.recv(1024).decode('utf-8')
            parts = request_message.split(' ')
            size = parts[0]
            command = parts[1]
            key = parts[2]
            if command == 'P':
                value = parts[3]
            else:
                value = None

            if command == 'R':
                total_operations += 1
                total_reads += 1
                if key in tuple_space:
                    value = tuple_space[key]
                    response_message = f"{(16 + len(key) + len(value)):03d} OK ({key}, {value}) read"
                else:
                    total_errors += 1
                    response_message = f"{(23 + len(key)):03d} ERR {key} does not exist"
            elif command == 'G':
                total_operations += 1
                total_gets += 1
                if key in tuple_space:
                    value = tuple_space[key]
                    del tuple_space[key]
                    response_message = f"{(19 + len(key) + len(value)):03d} OK ({key}, {value}) removed"
                else:
                    total_errors += 1
                    response_message = f"{(23 + len(key)):03d} ERR {key} does not exist"
            elif command == 'P':
                total_operations += 1
                total_puts += 1
                if key in tuple_space:
                    total_errors += 1
                    response_message = f"{(23 + len(key) + len(value)):03d} ERR {key} already exists"
                else:
                    tuple_space[key] = value
                    response_message = f"{(13 + len(key)):03d} OK {key} added"

            client_socket.sendall(response_message.encode('utf-8'))

    except Exception as e:
        print(f'Error in handling client {client_address}: {e}')
    finally:
        client_socket.close()
        print(f'Connection with {client_address} has been closed.')

def display_summary():
    global total_tuples
    global average_tuple_size
    global average_key_size
    global average_value_size

    while True:
        total_tuples = len(tuple_space)
        if total_tuples > 0:
            average_tuple_size = sum(len(key) + len(value) for key, value in tuple_space.items()) / total_tuples
            average_key_size = sum(len(key) for key in tuple_space.keys()) / total_tuples
            average_value_size = sum(len(value) for value in tuple_space.values()) / total_tuples
        else:
            average_tuple_size = 0
            average_key_size = 0
            average_value_size = 0

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
        time.sleep(10)

def start_server(hostname, port_number):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (hostname, port_number)
    server_socket.bind(server_address)
    server_socket.listen(5)
    print('Server is running and ready to accept multiple clients...')

    threading.Thread(target=display_summary).start()

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        print('Shutting down the server...')
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server('localhost', 51234)