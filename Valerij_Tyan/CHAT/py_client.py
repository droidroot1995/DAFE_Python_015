import socket
from threading import Thread
from py_classes import HOST, PORT, MAX_LENGTH_MSG


def listening_console():
    while True:
        msg = input()
        server.sendall(msg.encode())


def listening_host():
    while True:
        msg = server.recv(MAX_LENGTH_MSG)
        if msg:
            print(msg.decode())


if __name__ == '__main__':
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    server.connect((HOST, PORT))

    Thread(target=listening_console).start()
    Thread(target=listening_host).start()
