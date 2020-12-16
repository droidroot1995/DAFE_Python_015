from Socket import Socket
from threading import Thread
from os import system
from datetime import datetime

class Client(Socket):
    def __init__(self):
        super(Client, self).__init__()
        self.messages = []

    def set_up(self):
        try:
            self.connect(
                ("127.0.0.1", 1234)
            )
        except ConnectionRefusedError:
            print("Offline")
            exit(0)
        lis_thread = Thread(target = self.listen_socket)
        lis_thread.start()
        send_thread = Thread(target=self.send_data, args=(None,))
        send_thread.start()


    def listen_socket(self, listened_socket=None):
        while True:

            data = self.recv(1024)
            self.messages.append(f'{data.decode("utf-8")}\n')
            system("cls")
            for i in range(2 if len(self.messages)>2 else 0,len(self.messages) ):
                print(self.messages[i])


    def send_data(self, data):
        while True:
            to_send = (input(':::'))
            if to_send == '/quit':
                self.messages = []
                print("You have left the room")
            self.send(to_send.encode('utf-8'))

if __name__ == "__main__":
    client = Client()
    client.set_up()