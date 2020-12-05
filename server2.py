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
socket_list = []
address_info_list = []

print(f'Listening for connections on {IP}:{PORT}...')


# To pass to thread
def client_callback(_client_socket, _info):
    name = _client_socket.recv(1024)
    broadcast(name.decode("utf-8") + " has joined the chat", _client_socket)
    _client_socket.send("Welcome to LAM\n".encode("utf-8"))
    while True:
        try:
            msg = _client_socket.recv(1024)
            if msg:
                msg_str = msg.decode("utf-8")
                print(msg_str)
                broadcast_msg = msg_str
                broadcast(broadcast_msg, _client_socket)
            else:
                remove(_client_socket)
                print("client disconnected")
                break
        except:
            remove(_client_socket)
            print("client disconnected")
            return


def broadcast(msg, sender):
    for socks in socket_list:
        if socks != sender:
            try:
                socks.send(msg.encode("utf-8"))
            except:
                socks.close()
                remove(socks)


def remove(_client_socket: socket):
    if _client_socket in socket_list:
        socket_list.remove(_client_socket)


while True:
    try:
        (client_socket, info) = server_socket.accept()
        socket_list.append(client_socket)
        client_thread = threading.Thread(target=client_callback, args=(client_socket, info))
        client_thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        exit(0)
        break

server_socket.close()
