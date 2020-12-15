
import threading
from Socket import Socket

class User():
    def __init__(self, sock, name, room):
        self.sock = sock
        self.name = name
        self.is_connected = False
        self.room  = room
class Room():
    def __init__(self, user = None):
        self.users = []
        if user:
            self.users.append(user)
        self.history = ''

    def get_amount(self):
        return len(self.users)
    def add(self, u):
        self.users.append(u)
    def remove(self, name):
        print(name, self.users[0].name)
        for i in range(len(self.users)):
            if self.users[i].name == name:
                print(i)
                self.users.remove(self.users[i])

    def add_history(self, data):
        self.history = self.history + data +'\n'

    def is_in_room(self, name):
        for i in self.users:
            if i.name == name:
                return True
        return False


class Server(Socket):
    def __init__(self):
        super(Server, self).__init__()
        print("server is listening")
        self.users = []
        self.rooms = {'1':Room()}

    def get_amount(self):
        c = 0
        for i, v in self.rooms.items():
            c += v.get_amount()
        return c

    def set_up(self):
        self.bind(("127.0.0.1", 1234))
        self.listen()
        self.add_user()

    def send_data(self, data, room):
        self.rooms[room].add_history(data.decode('utf-8'))
        for i in self.rooms[room].users:
            i.sock.send(data)

    def listen_socket(self, user=None):
        while True:
            try:
                data = user.sock.recv(1024)
                data1 = data
                if str(data1.decode('utf-8')) == '/quit':
                    self.rooms[user.room].remove(user.name)
                    user.room = ''
                    self.ident_new(user.sock)
                data = user.name +': '+ str(data.decode('utf-8'))
                self.send_data(data.encode('utf-8'), user.room)
            except ConnectionResetError:
                if (self.get_amount()== 0):return
                self.rooms[user.room].remove(user.name)
                print("disconnected")

                return

    def ident_new(self, sock):
        sock.send(">Input room:".encode("utf-8"))
        room = (sock.recv(1024)).decode("utf-8")
        sock.send(">Input your name:".encode("utf-8"))
        name = sock.recv(1024).decode('utf-8')
        if room in self.rooms:
            while self.rooms[room].is_in_room(name):
                sock.send(">Please, choose another name: ".encode("utf-8"))
                name = sock.recv(1024).decode('utf-8')
            self.rooms[room].add(User(sock, name, room))
        else:
            self.rooms[room] = Room( User(sock, name, room))
        sock.send(self.rooms[room].history.encode("utf-8"))
        self.send_data(((str(name) + " is connected to room " + room).encode("utf-8")), room)

        print(self.rooms[room].history)
        accepted = threading.Thread(target=self.listen_socket, args=(User(sock, name, room),))
        accepted.start()

    def add_user(self):
        while True:
            user_sock, address = self.accept()
            name = threading.Thread(target=self.ident_new, args=[user_sock,])
            name.start()


if __name__ == '__main__':
    s= Server()
    s.set_up()
