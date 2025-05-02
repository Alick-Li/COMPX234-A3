import socket

tuple_space = {}

total_clients = 0
total_operations = 0
total_reads = 0
total_gets = 0
total_puts = 0
total_errors = 0

def handle_client(client_socket, client_address):
    total_clients += 1

    try:
        while True:
            request_message = client_socket.recv(1024).decode('utf-8')

            size = request_message.split(' ')[0]
            command = request_message.split(' ')[1]
            key = request_message.split(' ')[2]
            if command == 'P':
                value = request_message.split(' ')[3]
            else:
                value = None

            if command == 'R':
                total_operations += 1
                total_reads += 1

                if key in tuple_space:
                    response_message = f"f'{(16 + len(key) + len(value)):03d}' OK ({key}, {value}) read"
                else:
                    total_errors += 1
                    response_message = f"f'{(23 + len(key)):03d}' ERR {key} does not exist"
            
            elif command == 'G':
                total_operations += 1
                total_gets += 1

                if key in tuple_space:
                    response_message = f"f'{(19 + len(key) + len(value)):03d}' OK ({key}, {value}) removed"
                else:
                    total_errors += 1
                    response_message = f"f'{(23 + len(key)):03d}' ERR {key} does not exist"
            
            elif command == 'P':
                total_operations += 1
                total_puts += 1

                if key in tuple_space:
                    total_errors += 1
                    response_message = f"f'{(23 + len(key) + len(value)):03d}' ERR {key} already exists"                    
                else:
                    tuple_space[key] = value
                    response_message = f"f'{(13 + len(key)):03d}' OK {key} added"
            
            client_socket.sendall(response_message.encode('utf-8'))
                
    except Exception as e:
        print(f'Error in handling client {client_address}: {e}')
    finally:
        client_socket.close()
        print(f'Connection with {client_address} has been closed.')

def start_server(hostname, port_number):
    hostname = hostname
    port_number = port_number

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (hostname, port_number)
    server_socket.bind(server_address)
    server_socket.listen(5)
    print('Server is running and ready to accept multiple clients...')

    try:
        while True:
            raise NotImplementedError
    except KeyboardInterrupt:
        print('Shutting down the server...')
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server('localhost', 51234)