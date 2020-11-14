import socket
import select
import sys

if len(sys.argv) != 3:
    print("Usage: python3 server.py <IP> <port>")
    exit(1)

HEADER_LENGTH = 25

IP = str(sys.argv[1])
PORT = int(sys.argv[2])


# Creating a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ is Socket Option
# SOL_ is Socket Option Level
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    # Create an address with IP address and port
    server_socket.bind((IP, PORT))
except socket.gaierror as err:
    print('Err: Can not bind socket\nCause: ', err.args[1])
    exit(1)

# Listen for new connections
server_socket.listen()
sockets_list = [server_socket]


# Add all connected clients in a Dictionary, Really Sonu?
# TODO: Create JSON and add it to Database
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')


# Handel all messages
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        # Close connection if length of message_header is 0
        # Could use socket.close() or socket.shutdown(socket.SHUT_RDWR) instead
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    # Using wildcard except TODO: Do not use bare except
    except:
        # Wait for any Exception such as KeyboardInterrupt and call socket.close()
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address,
                                                                            user['data'].decode('utf-8')))
        else:
            message = receive_message(notified_socket)
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
