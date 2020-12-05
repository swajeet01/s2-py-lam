import socket
import sys
import threading

if len(sys.argv) != 3:
    print("Usage: python3 server.py <IP> <PORT>")
    print("Now binding on default IP(127.0.0.1) and PORT(7066)")
    IP = "127.0.0.1"
    PORT = 7066
else:
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
# as client_socket: name pair
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')


# callback to pass to thread
# This Thread is responsible for message transfers b/w server and client
def client_callback(_client_socket, _info):
    name = _client_socket.recv(1024)
    # broadcast message to everyone that a new client is joined
    name_str = name.decode("utf-8")
    broadcast(name_str + " has joined the chat", _client_socket)
    print("LOG:", name_str, "joined")
    clients[_client_socket] = name_str
    users = ""
    for name in clients.values():
        users += (name + ", ")
    _client_socket.send("Welcome to LAM".encode("utf-8"))
    if len(clients) != 1:
        _client_socket.send(("[" + users[:-2] + "] are here.").encode("utf-8"))
    while True:
        try:
            msg = _client_socket.recv(1024)
            if msg:
                msg_str = msg.decode("utf-8")
                print(msg_str)
                broadcast_msg = msg_str
                broadcast(broadcast_msg, _client_socket)
            else:
                print("LOG:", clients[_client_socket], " disconnected")
                remove(_client_socket)
                break
        except:
            print("LOG:", clients[_client_socket], " disconnected")
            remove(_client_socket)
            return
    return


def broadcast(msg, sender):
    for (client, name) in clients.items():
        if client != sender:
            try:
                client.send(msg.encode("utf-8"))
            except:
                client.close()
                remove(client)


def remove(_client_socket: socket):
    if _client_socket in clients:
        broadcast(clients.pop(_client_socket) + " has left the chat", _client_socket)


while True:
    try:
        (client_socket, info) = server_socket.accept()
        clients[client_socket] = "Unknown"
        client_thread = threading.Thread(target=client_callback, args=(client_socket, info))
        client_thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        exit(0)
        break

server_socket.close()
