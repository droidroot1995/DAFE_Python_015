import socket
import threading


HOST = '127.0.0.1'
PORT = 1234
MAX_LENGTH_MSG = 255
MAX_LENGTH_HIST = 128


class Room:
    def __init__(self, name):
        self.name = name
        self.users = []
        self.history_messages = [MAX_LENGTH_HIST]

    def message(self, message, author=None):
        author = author.name.encode() if author else b'host'
        message = author + b': ' + message.encode()
        for user in self.users:
            user.user_socket.sendall(message)
        if len(self.history_messages) < 128:
            self.history_messages.append(message)
        else:
            self.history_messages.remove(1)
            self.history_messages.pop(0)

    def get_history(self):
        for i in range(len(self.history_messages)):
            nwstr = '\n'.encode()
            self.users[len(self.users)-1].user_socket.sendall(self.history_messages[i] + nwstr)


class Chat:
    def __init__(self):
        # rooms' list
        self.rooms = {}

    def handle(self, user, message):
        if '/create' == message.split()[0]:
            if len(message.split()) > 1:
                # Is the user in other rooms?
                if user.room:
                    user.room.users.remove(user)
                    user.room = None
                room_name = message.split()[1]
                room = Room(room_name)
                # Is there a room with that name?
                if room.name in self.rooms:
                    user.user_socket.sendall('Name is already in use'.encode())
                else:
                    room.users.append(user)
                    self.rooms[room_name] = room
                    user.room = room
                    print('created room <' + room_name + '>')
                    self.rooms[room_name].message(message='<' + user.name + '>' + ' created room <' + room_name + '>\n')
                    self.rooms[room_name].message(message='User ' + '<' + user.name + '>' + ' joined to the <' + self.rooms[room_name].name + '>')
            else:
                user.user_socket.sendall('The wrong trying! Missing room\'s name'.encode())
        elif '/join' == message.split()[0]:
            if len(message.split()) > 1:
                if user.room:
                    user.room.users.remove(user)
                    user.room.message(message='<' + user.name + '>' + ' left ' + '<' + user.room.name + '>')
                    user.room = None
                room_name = message.split()[1]
                current_room = self.rooms[room_name]
                # user.user_socket.sendall(f'{user}'.encode())
                # user.user_socket.sendall(f'<{user.name}>'.encode())
                b = False
                for i in range(len(current_room.users)):
                    if user.name == current_room.users[i].name:
                        b = True
                if b:
                    user.user_socket.sendall('Nickname is already in use'.encode())
                else:
                    if current_room.name in self.rooms:
                        current_room.users.append(user)
                        user.room = current_room
                        current_room.get_history()
                        current_room.message(message='User ' + '<' + user.name + '>' + ' joined to the <' + current_room.name + '>')
                    else:
                        user.user_socket.sendall('The wrong trying! No room with that name!'.encode())
            else:
                user.user_socket.sendall('The wrong trying! Missing room\'s name'.encode())
        elif '/set_nick' == message.split()[0]:
            if len(message.split()) > 1:
                user.name = message.split()[1]
                user.user_socket.sendall(f'Welcome, <{user.name}>!'.encode())
            else:
                user.user_socket.sendall('The wrong trying! Missing nickname'.encode())
        elif '/room_list' == message.split()[0]:
            if len(self.rooms) > 0:
                for i in self.rooms:
                    name_room = self.rooms[i].name
                    user.user_socket.sendall(f'<{name_room}>\n'.encode())
            else:
                user.user_socket.sendall('No rooms has been created!'.encode())
        elif '/user_list_in' == message.split()[0]:
            if len(message.split()) > 1:
                name_room = message.split()[1]
                room = Room(name_room)
                if room.name in self.rooms:
                    for i in range(len(self.rooms[name_room].users)):
                        nm_rm = self.rooms[name_room].users[i].name
                        user.user_socket.sendall(f'<{nm_rm}>\n'.encode())
                else:
                    user.user_socket.sendall('The wrong trying! The wrong room\'s name!'.encode())
            else:
                user.user_socket.sendall('The wrong trying! Missing room\'s name'.encode())
        elif user.room:
            print(user.name + ': ' + message)
            user.room.message(message, user)


class User:
    def __init__(self, user_socket, name='new'):
        self.user_socket = user_socket
        self.name = name
        self.room = None
