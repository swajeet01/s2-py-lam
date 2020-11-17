import socket
import select
import sys

if len(sys.argv) != 3:
    print("Usage: python3 client.py <IP> <port>")
    exit(1)

IP = str(sys.argv[1])
PORT = int(sys.argv[2])

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((IP, PORT))

name = input("Your name: ")

while True:
    sockets_list = [sys.stdin, server_socket]
    read_sockets, write_sockets, exception_sockets = select.select(sockets_list, [], [])
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            msg = notified_socket.recv(1024)
            print(msg.decode("utf-8"), end='')
        else:
            msg = input()
            if msg.lower() == 'bye':
                server_socket.close()
                exit(1)
            server_socket.send(("\n" + name + ": " + msg).encode("utf-8"))
