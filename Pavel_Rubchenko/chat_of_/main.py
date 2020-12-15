import socket
import struct
import threading
from datetime import datetime


class Constants:
    ADD_MESSAGE_RESULT           = 10
    ADD_MESSAGE_WRONG_COMMAND    = 11
    ADD_MESSAGE_NO_ROOM          = 12
    ADD_MESSAGE_OK               = 13
    ADD_MESSAGE_ACCESS_VIOLATION = 14

    JOIN_RESULT                  = 20
    JOIN_WRONG_COMMAND           = 21
    JOIN_NO_ROOM                 = 22
    JOIN_OK                      = 23
    JOIN_NAME_IN_USE             = 24

    LEAVE_RESULT                 = 30
    LEAVE_NO_ROOM                = 31
    LEAVE_OK                     = 32
    LEAVE_NOT_IN_ROOM            = 33

    CREATE_ROOM_RESULT           = 40
    CREATE_ROOM_ALREADY_EXISTS   = 41
    CREATE_ROOM_OK               = 42

    LIST_RESULT                  = 50
    LIST_OK                      = 51

    NEW_MESSAGE                  = 60

    UNKNOWN_COMMAND              = 99

class Config:
    @staticmethod
    def get_room_story_length() -> int:
        return 10

    @staticmethod
    def get_server_port() -> int:
        return 32000

class Message:
    def __init__(self, text: str, author: str):
        self.__text = text
        self.__date = datetime.now()
        self.__author = author

    # получить форматированное сообщение
    def get_formatted_message(self) -> str:
        return "({}) {}:{}".format(self.__date.strftime("%Y:%m%d %H:%M:%S"), self.__author, self.__text)

class Client(threading.Thread):
    def __init__(self, connection, server, client_id):
        threading.Thread.__init__(self)

        self.__client_id = client_id
        self.__server = server
        self.__connection = connection
        self.__is_active = True

    def get_socket(self):
        return self.__connection;

    # остановить работу клиента
    def stop(self):
        self.__is_active = False

    # цикл обработки сообщений от клиента
    def run(self):
        while self.__is_active:
            try:
                data = self.__connection.recv(1024)
                data = data.decode('utf-8')

                self.__handle_message(data)

            except BaseException as e:
                print(e)
                print("[Client {}] Unhandled exception during handle message for client".format(self.__client_id))
                break

    # обработать входящее сообщение data
    def __handle_message(self, data):
        cmd = data.split(' ', 1)

        if cmd[0] == '/subscribe' and len(cmd) == 2:
            self.__add_to_room(cmd[1])
        elif cmd[0] == '/unsubscribe' and len(cmd) == 2:
            self.__remove_from_room(cmd[1])
        elif cmd[0] == '/create' and len(cmd) == 2:
            self.__create_room(cmd[1])
        elif cmd[0] == '/list':
            self.__list_subscriptions()
        elif cmd[0] == '/send' and len(cmd) == 2:
            self.__add_message(cmd[1])
        elif cmd[0] == '/leave':
            self.__close_connection()
        else:
            print("[Client] Cannot parse incoming command: {}".format(cmd))

            data = struct.pack("i", Constants.UNKNOWN_COMMAND)
            self.__connection.send(data)

    # опубликовать сообщунеие <str> в канале <room>
    # /send <room> <str>
    def __add_message(self, cmd):
        data = struct.pack("i", Constants.ADD_MESSAGE_RESULT)
        self.__connection.send(data)

        params = cmd.split(' ', 1)
        if len(params) != 2:
            print("[Client {}] Wrong argument count for /send command ({})".format(self.__client_id, cmd))
            data = struct.pack("i", Constants.ADD_MESSAGE_WRONG_COMMAND)
            self.__connection.send(data)
            return

        room_name = params[0]
        message = params[1]

        room = self.__server.get_room(room_name)
        if room is None:
            print("[Client {}] Cannot send message to room. No such room found ({})".format(self.__client_id, room_name))
            data = struct.pack("i", Constants.ADD_MESSAGE_NO_ROOM)
            self.__connection.send(data)
            return

        room.add_message(self, message)

    # добавить участника в комнату
    # /subscribe <name> <room>
    def __add_to_room(self, cmd):
        data = struct.pack("i", Constants.JOIN_RESULT)
        self.__connection.send(data)

        params = cmd.split(' ')
        if len(params) != 2:
            print("[Client {}] Wrong argument count for /subscribe command ({})".format(self.__client_id, cmd))
            data = struct.pack("i", Constants.JOIN_WRONG_COMMAND)
            self.__connection.send(data)
            return

        room_name = params[0]
        user_name = params[1]
        room = self.__server.get_room(room_name)
        if room is None:
            print("[Client {}] Cannot join to room. No such room found ({})".format(self.__client_id, room_name))
            data = struct.pack("i", Constants.JOIN_NO_ROOM)
            self.__connection.send(data)
            return

        if room.add_participant(self, user_name):
            print("[Client {}] Client joined to {} as {}".format(self.__client_id, room_name, user_name))

    # покинуть комнату
    # /unsubscribe <room>
    def __remove_from_room(self, cmd):
        data = struct.pack("i", Constants.LEAVE_RESULT)
        self.__connection.send(data)

        room_name = cmd
        room = self.__server.get_room(room_name)
        if room is None:
            print("[Client {}] Cannot leave room. No such room found ({})".format(self.__client_id, room_name))
            data = struct.pack("i", Constants.LEAVE_NO_ROOM)
            self.__connection.send(data)
            return

        if room.remove_participant(self):
            print("[Client {}] User leave room {}".format(self.__client_id, room_name))
            data = struct.pack("i", Constants.LEAVE_OK)
            self.__connection.send(data)

    # создать комнату
    # /create <room>
    def __create_room(self, cmd):
        data = struct.pack("i", Constants.CREATE_ROOM_RESULT)
        self.__connection.send(data)

        room_name = cmd
        room = self.__server.get_room(room_name)

        if room is not None:
            print("[Client {}] Cannot create room. Room {} already exists".format(self.__client_id, room_name))
            data = struct.pack("i", Constants.CREATE_ROOM_ALREADY_EXISTS)
            self.__connection.send(data)
            return

        print("[Client {}] Room {} created".format(self.__client_id, room_name))
        self.__server.create_room(room_name)
        data = struct.pack("i", Constants.CREATE_ROOM_OK)
        self.__connection.send(data)

    # просмотреть список подписок
    # /ls
    def __list_subscriptions(self):
        data = struct.pack("i", Constants.LIST_RESULT)
        self.__connection.send(data)

        subscriptions = []
        for room in self.__server.get_rooms():
            for (c, name) in room.get_participant():
                if c == self:
                    subscriptions.append(room.get_name())

        print("[Client {}] Get subscription for client".format(self.__client_id))
        data = struct.pack("i", Constants.LIST_OK)
        self.__connection.send(data)
        data = struct.pack("i", len(subscriptions))
        self.__connection.send(data)
        for room in subscriptions:
            self.__connection.send(room.encode())

    # завершить работу клиента
    def __close_connection(self):
        print("[Client {}] Client finished".format(self.__client_id))
        self.__is_active = False
        for room in self.__server.get_rooms():
            room.remove_participant(self)

class Room:
    def __init__(self, name : str):
        self.__name = name
        self.__messages = []
        self.__participants = []
        self.__message_lock = threading.Lock()
        self.__participant_lock = threading.Lock()

    # получить список участников комнаты
    def get_participant(self):
        return self.__participants;

    # добавить сообщение str от клиента client в комнату
    # вначале мы должны пройти по всем учатсникам комнаты и определить имя клиента в команте
    # затем мы проверяем, что количество сообщений в команте не превысило указанного числа (при необходимости отсекаем старые)
    # далее добавляем сообщение и рассылаем его всем подписчикам
    def add_message(self, client: Client, message: str) -> bool:
        username = None
        for (c, name) in self.__participants:
            if c == client:
                username = name

        if username is None:
            print("[Channel {}] Cannot add message, because author does not belong to channel".format(self.__name))
            data = struct.pack("i", Constants.ADD_MESSAGE_ACCESS_VIOLATION)
            client.get_socket().send(data)
            return False

        formatted_message = Message(message, username)

        with self.__message_lock:
            if len(self.__messages) > Config.get_room_story_length():
                self.__messages = self.__messages[len(self.__messages) - Config.get_room_story_length():]

            self.__messages.append(formatted_message)

        data = struct.pack("i", Constants.ADD_MESSAGE_OK)
        client.get_socket().send(data)

        header_data = struct.pack("i", Constants.NEW_MESSAGE)
        message_data = "[{}] {}".format(self.__name, formatted_message.get_formatted_message())

        with self.__participant_lock:
            for (c, name) in self.__participants:
                c.get_socket().send(header_data)
                c.get_socket().send(message_data.encode())

        return True

    # добавить клиента client в команту под псевдонимом name
    # вначале проходим по всем участникам комнаты и проверяем, что такое имя еще не используется
    # затем добавляем нового подписчика и отправляем ему историю переписки в комнате
    def add_participant(self, client: Client, new_name: str) -> bool:
        with self.__participant_lock:
            for (c, name) in self.__participants:
                if name == new_name:
                    print("[Channel {}] Cannot add new participant with name {}. Given name already in use".format(self.__name, new_name))
                    data = struct.pack("i", Constants.JOIN_NAME_IN_USE)
                    client.get_socket().send(data)
                    return False;

            print("[Channel {}] New participant: {}".format(self.__name, new_name))
            self.__participants.append((client, new_name))

        data = struct.pack("i", Constants.JOIN_OK)
        client.get_socket().send(data)

        print("[Channel {}] Send channel history ({}) to new participant".format(self.__name, len(self.__messages)))
        data = struct.pack("i", len(self.__messages))
        client.get_socket().send(data)
        for message in self.__messages:
            data = "[{}] {}".format(self.__name, message.get_formatted_message())
            client.get_socket().send(data.encode())

        return True

    # удалить участника из канала
    def remove_participant(self, client: Client) -> bool:
        with self.__participant_lock:
            for (c, name) in self.__participants:
                if c == client:
                    print("[Channel {}] Participant {} leave channel".format(self.__name, name))
                    self.__participants.remove((client, name))
                    return True

        print("[Channel {}] Cannot remove participant. No such participant in this channel".format(self.__name))
        data = struct.pack("i", Constants.LEAVE_NOT_IN_ROOM)
        client.get_socket().send(data)
        return False

    # получить имя канала
    def get_name(self) -> str:
        return self.__name

class Server:
    def __init__(self):
        self.__rooms = []
        self.__connections = []

    # получить комнату по имени name
    def get_room(self, name: str) -> Room:
        for room in self.__rooms:
            if room.get_name() == name:
                return room

        return None

    # получить все комнаты
    def get_rooms(self):
        return self.__rooms

    # создать комнату с именем name
    def create_room(self, name: str):
        room = Room(name)
        self.__rooms.append(room)

    # точка входа
    # открываем сокет на прослушивание входящих сообщений
    # для каждого подключения стартуем поток (обработчик client.run)
    def main(self):
        incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        incoming_socket.bind(('0.0.0.0', Config.get_server_port()))
        incoming_socket.listen(10)
        client_id = 0

        print("[Server] Server started :{}".format(Config.get_server_port()))

        while True:
            try:
                connection, address = incoming_socket.accept()
                print("[Server] New connection from {}".format(address))

                client = Client(connection, self, client_id)
                self.__connections.append(client)
                client.start()

                client_id = client_id + 1

            except KeyboardInterrupt:
                break

            except BaseException as e:
                print(e)
                print("[Server] Server stopped due unhandled exception")
                break

        incoming_socket.close()


if __name__ == '__main__':
    Server().main()