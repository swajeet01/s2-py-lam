import socket
import select

HEADER_LENGTH = 25

IP = "127.0.0.1"
PORT = 7066

# socket bna rha hu
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ ka matlab socket option
# SOL_ ka matlab socket option level
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#ip address or port number ko combine kar ke ek address bna rha hu
server_socket.bind((IP, PORT))

# ye jb bhi koi  new connection aayega uko listen karega

server_socket.listen()
sockets_list = [server_socket]


# jitna v device connect hoga usko dictnory me store karba rhe hai
# bad me agar tumko database ka chull rhega to isko json me convert kar ke databae me store karwa lena
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# jitna v messages ayega ya jayega usko ye function handle arega

def receive_message(client_socket):

    try:


        message_header = client_socket.recv(HEADER_LENGTH)

        # agar message ka len nhi hua to connection close ho jayega
        # iske jagah per hm socket.close() ya  socket.shutdown(socket.SHUT_RDWR) v kar sakte the

        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # agar iske alawa script me koi dikkat aayega like user ctrl + c dwa diya ya script band kar diya ya koi or exceptation to usko
        # ye handle karega simple call kar dga secket.close();
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

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

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