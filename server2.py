import socket
import sys
import threading

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
    print('Err: Can not bind socket\nCause:', err.args[1])
    exit(1)

# Listen for new connections
server_socket.listen()
sockets_list = []

print(f'Listening for connections on {IP}:{PORT}...')


# To pass to thread
def client_callback(client_socket, info):
    client_socket.send("Welcome to LAM\nYou: ".encode("utf-8"))
    while True:
        msg = client_socket.recv(1024)
        if msg:
            msg_str = msg.decode("utf-8")
            print(msg_str, end='')
            broadcast_msg = msg_str
            broadcast(broadcast_msg, client_socket)
        else:
            remove(client_socket)


def broadcast(msg, sender):
    for socks in sockets_list:
        if socks != sender:
            try:
                socks.send((msg + "\nYou: ").encode("utf-8"))
            except:
                socks.close()
                remove(socks)


def remove(client_socket):
    if client_socket in sockets_list:
        sockets_list.remove(client_socket)


while True:
    try:
        (client_socket, info) = server_socket.accept()
        sockets_list.append(client_socket)
        print("Log: A new user connected")
        client_thread = threading.Thread(target=client_callback, args=(client_socket, info))
        client_thread.start()
        broadcast("New user connected", client_socket)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        break

server_socket.close()
