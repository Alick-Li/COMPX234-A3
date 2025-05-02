import socket
import threading
import time

def client_task(hostname, port_number, pathname):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (hostname, port_number)
        client_socket.connect(server_address)

        with open(pathname, 'r') as file:
            for line in file:
                parts = line.strip().split(' ')
                command = parts[0]
                key = parts[1]
                value = ' '.join(parts[2:]) if command == 'PUT' else None

                if command in ['READ', 'GET']:
                    if len(key) > 970:
                        print('Error: Key size exceeds 970 characters')
                        continue
                elif command == 'PUT':
                    if len(key + ' ' + value) > 970:
                        print('Error: Collated size exceeds 970 characters')
                        continue

                if command == 'READ':
                    request_message = f"{(6 + len(key)):03d} R {key}"
                elif command == 'GET':
                    request_message = f"{(6 + len(key)):03d} G {key}"
                elif command == 'PUT':
                    request_message = f"{(7 + len(key) + len(value)):03d} P {key} {value}"

                client_socket.sendall(request_message.encode('utf-8'))

                response_message = client_socket.recv(1024).decode('utf-8')
                print(f'{pathname[14:22]} received: {response_message}')

    except Exception as e:
        print(f"Error for {pathname[14:22]}: {e}")
    finally:
        client_socket.close()

def main():
    clients = []

    for i in range(1, 11):
        t = threading.Thread(target=client_task, args=('localhost', 51234, f'Request Files\\client_{i}.txt'))
        clients.append(t)
        t.start()
        time.sleep(0.1)

    for t in clients:
        t.join()

if __name__ == "__main__":
    main()