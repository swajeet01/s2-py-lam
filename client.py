import socket
import select
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

# TODO: name it idiot
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

name = input("Your name: ")
s.send(name.encode("utf-8"))

stream_list = [sys.stdin, s]

while True:
    try:
        read_sockets, write_sockets, exception_sockets = select.select(stream_list, [], [])
        for notified_socket in read_sockets:
            if notified_socket == s:
                msg = notified_socket.recv(1024)
                msg_str = msg.decode("utf-8")
                print(msg_str)
            else:
                msg = input()
                if msg.lower() == "c:bye":
                    s.close()
                    print("You left")
                    exit(1)
                s.send((name + ": " + msg).encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        s.close()
        print("You left")
        exit(1)
