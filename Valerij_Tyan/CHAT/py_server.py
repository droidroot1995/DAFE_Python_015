import socket
import threading
from py_classes import User, Chat, HOST, PORT, MAX_LENGTH_MSG


def client_thread(client_user):
    while True:
        # msg - message
        msg = client_user.user_socket.recv(MAX_LENGTH_MSG)
        if msg:
            handle.handle(client_user, msg.decode())
        else:
            client_user.user_socket.close()
            users.remove(client_user)


def print_rules(usr):
    usr.user_socket.sendall('Welcome to the club, buddy!\n'.encode())
    usr.user_socket.sendall('Commands\' list:\n'.encode())
    usr.user_socket.sendall('/set_nick <nickname> (without <>) - to set nickname\n'.encode())
    usr.user_socket.sendall('/create <room\'s name> (without <>) - to create room\n'.encode())
    usr.user_socket.sendall('/join <room\'s name> (without <>) - to join room\n'.encode())
    usr.user_socket.sendall('/room_list - to watch rooms\' list\n'.encode())
    usr.user_socket.sendall('/user_list <room_name>\n'.encode())


if __name__ == '__main__':
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    server.bind((HOST, PORT))
    server.listen()
    print('server_listening...')

    users = []
    handle = Chat()

    while True:
        user_socket, address = server.accept()
        user = User(user_socket)
        users.append(user)
        print_rules(user)
        new_thread = threading.Thread(target=client_thread, args=(user,))
        new_thread.start()
