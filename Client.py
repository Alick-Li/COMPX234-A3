import socket
import threading
import time

def client_task(hostname, port_number, pathname):
    hostname = hostname
    port_number = port_number
    pathname = pathname

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (hostname, port_number)
        client_socket.connect(server_address)

        with open(pathname, 'r') as file:
            for line in file:
                command = line.strip().split(' ')[0]
                key = line.strip().split(' ')[1]
                if command == 'PUT':
                    value = line.strip().split(' ')[2:]
                else:
                    value = None

                if len(key + ' ' + value) <= 970:
                    if command == 'READ':
                        request_message = f"f'{(6 + len(key)):03d}' R {key}"
                    elif command == 'GET':
                        request_message = f"f'{(6 + len(key)):03d}' G {key}"
                    elif command == 'PUT':
                        request_message = f"f'{(7 + len(key) + len(value)):03d}' P {key} {value}"
                else:
                    print('Error: Collated size exceed 970 characters')
                client_socket.sendall(request_message.encode('utf-8'))

                response_message = client_socket.recv(1024).decode('utf-8')
                print(f'{pathname[14:21]} received: {response_message}')
    except Exception as e:
        print(f"Error for {pathname[14:21]}: {e}")
    finally:
        client_socket.close()

def main():
    clients = []
    for i in range(1, 11):
        t = threading.Thread(target=client_task, args=('localhost', 51234, f'Request Files\\client{i}.txt'))
        clients.append(t)
        t.start()
        time.sleep(0.1)
    for t in clients:
        t.join()

if __name__ == "__main__":
    main()