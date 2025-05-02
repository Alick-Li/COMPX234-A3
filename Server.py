import socket

def handle_client(client_socket, client_address):
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