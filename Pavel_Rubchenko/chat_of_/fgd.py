import select
from collections import deque
import socket
import struct
import threading

class Constants:
    ADD_MESSAGE_RESULT = 10
    ADD_MESSAGE_WRONG_COMMAND = 11
    ADD_MESSAGE_NO_ROOM = 12
    ADD_MESSAGE_OK = 13
    ADD_MESSAGE_ACCESS_VIOLATION = 14

    JOIN_RESULT = 20
    JOIN_WRONG_COMMAND = 21
    JOIN_NO_ROOM = 22
    JOIN_OK = 23
    JOIN_NAME_IN_USE = 24

    LEAVE_RESULT = 30
    LEAVE_NO_ROOM = 31
    LEAVE_OK = 32
    LEAVE_NOT_IN_ROOM = 33

    CREATE_ROOM_RESULT = 40
    CREATE_ROOM_ALREADY_EXISTS = 41
    CREATE_ROOM_OK = 42

    LIST_RESULT = 50
    LIST_OK = 51

    NEW_MESSAGE = 60

    UNKNOWN_COMMAND = 99

class Client(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connection.connect(('127.0.0.1', 32000))

        self.__outcoming_commands = deque()
        self.__is_active = False

    def add_command(self, command: str):
       self.__outcoming_commands.append(command)

    def stop(self):
        self.__is_active = False
        self.__connection.close()

    def run(self):
        self.__is_active = True

        while self.__is_active:
            if len(self.__outcoming_commands) > 0:
                cmd = self.__outcoming_commands.popleft()
                self.__connection.send(cmd.encode())

            ready = select.select([self.__connection], [], [], 1)

            if ready[0]:
                packer = struct.Struct('i')
                response = self.__connection.recv(packer.size)
                code = packer.unpack(response)[0]

                print(code)

                if code == Constants.ADD_MESSAGE_RESULT:
                    self.__handle_add_message_response()
                elif code == Constants.JOIN_RESULT:
                    self.__handle_join_response()
                elif code == Constants.LEAVE_RESULT:
                    self.__handle_leave_response()
                elif code == Constants.CREATE_ROOM_RESULT:
                    self.__handle_create_room_response()
                elif code == Constants.LIST_RESULT:
                    self.__handle_list_response()
                elif code == Constants.NEW_MESSAGE:
                    message = self.__connection.recv(1024).decode('utf-8')
                    print(message)
                elif code == Constants.UNKNOWN_COMMAND:
                    print("Unknown command")
                else:
                    print("Unknown response {}".format(code))

    def __handle_add_message_response(self):
        packer = struct.Struct('i')
        response = self.__connection.recv(packer.size)
        subcode = packer.unpack(response)[0]

        if subcode == Constants.ADD_MESSAGE_WRONG_COMMAND:
            print("")
        elif subcode == Constants.ADD_MESSAGE_NO_ROOM:
            print("No such room")
        elif subcode == Constants.ADD_MESSAGE_OK:
            pass
        elif subcode == Constants.ADD_MESSAGE_ACCESS_VIOLATION:
            print("Invalid command format (to send message use /send room_name message")

    def __handle_join_response(self):
        packer = struct.Struct('i')
        response = self.__connection.recv(packer.size)
        subcode = packer.unpack(response)[0]

        if subcode == Constants.JOIN_WRONG_COMMAND:
            print("Invalid command format (to join use /subscribe room_name user_name")
        elif subcode == Constants.JOIN_NO_ROOM:
            print("No such room")
        elif subcode == Constants.JOIN_OK:
            print("You joined to selected room")

            data = self.__connection.recv(packer.size)
            messagecount = packer.unpack(data)[0]
            while messagecount > 0:
                message = self.__connection.recv(1024).decode('utf-8')
                print(message)
                messagecount = messagecount - 1
        elif subcode == Constants.JOIN_NAME_IN_USE:
            print("Pick another name. This one already in use")

    def __handle_leave_response(self):
        packer = struct.Struct('i')
        response = self.__connection.recv(packer.size)
        subcode = packer.unpack(response)[0]

        if subcode == Constants.LEAVE_NO_ROOM:
            print("No such room")
        elif subcode == Constants.LEAVE_OK:
            print("You just left room")
        elif subcode == Constants.LEAVE_NOT_IN_ROOM:
            print("You does not subscribed to this room")

    def __handle_create_room_response(self):
        packer = struct.Struct('i')
        response = self.__connection.recv(packer.size)
        subcode = packer.unpack(response)[0]

        if subcode == Constants.CREATE_ROOM_ALREADY_EXISTS:
            print("Room with same name already exist")
        elif subcode == Constants.CREATE_ROOM_OK:
            print("Room created")

    def __handle_list_response(self):
        packer = struct.Struct('i')
        response = self.__connection.recv(packer.size)
        subcode = packer.unpack(response)[0]

        if subcode == Constants.LIST_OK:
            print("Your subscriptions:")
            data = self.__connection.recv(packer.size)
            subscriptionscount = packer.unpack(data)[0]
            while subscriptionscount > 0:
                name = self.__connection.recv(1024).decode('utf-8')
                print(name)
                subscriptionscount = subscriptionscount - 1

def print_help():
    print("Available commands:")
    print("/create channel_name - to create new channel with name channel_name. channel_name - string without spaces")
    print("/subscribe channel_name username - to subscribe to the channel_name channel with username name. channel_name and username - string without spaces")
    print("/unsubscribe channel_name - unsubscribe from channel with name channel_name. channel_name - string without spaces")
    print("/list - to display list of susbscribed channels")
    print("/send channel_name message - to send message with text message to channel with name channel_name. channel_name - string without space")
    print("/leave - to close connection and exit")


def main():
    print_help()
    client = Client()
    client.start()

    while True:
        message = input().strip()
        cmd = message.split(' ')
        if cmd[0] == '/leave':
            break

        client.add_command(message)

    client.stop()


if __name__ == "__main__":
    main()
