import socket

def start_server():
    host = 'localhost'
    port = 51234

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(host, port)
    server_socket.listen(5)

    try:
        while True:
            raise NotImplementedError
    except KeyboardInterrupt:
        print('Server shutting down...')
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()