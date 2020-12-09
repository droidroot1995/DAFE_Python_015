import socket, time, threading

HISTORY_LEN = 128   # max quantity of messages in history of chat
port = 0
rooms = []          # array of rooms


def room(name, port):
    host = socket.gethostbyname(socket.gethostname())

    clients = []
    history = []

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # preferences of server
    s.bind((host, port))                                    # set preferences

    quit = False
    print("[Server Started]", (host, port))

    while not quit:
        try:
            show_messages = True
            data, address = s.recvfrom(255)         # max size of message

            if address not in clients:
                clients.append(address)
                for el in history:
                    s.sendto(el.encode("utf-8"), address)

            devide = data.decode("utf-8").split(":")
            if len(devide) == 3:
                if devide[2] == "/change_room" or devide[2] == "/quit":   # /change_room - to change room, /quit - to quit server
                    clients.remove(address)
                    show_messages = False


            atime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
            if show_messages:
                msg = "[" + address[0] + "]=[" + str(address[1]) + "]=[" + atime + "]/ " + data.decode("utf-8")
                print(msg)
                if len(history) > HISTORY_LEN:
                    history.pop(0)
                history.append(data.decode("utf-8"))


            for client in clients:
                if address != client:
                    s.sendto(data, client)
        except:
            print("\n[Server stopped]")
            quit = True

    s.close()


def main():
    print("Server started")

    rooms = []
    rooms_names = {}
    host = socket.gethostbyname(socket.gethostname())

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = (host, 9089)
    s.bind(server)
    while True:
        data, address = s.recvfrom(255)
        try:
            port = 9090 + int(data.decode("utf-8"))
            if port >= 2**16 or port <9090:
                raise OverflowError

            if not port in rooms:
                print("Created room")
                rm = threading.Thread(target=room, args=("tryz", port))
                rm.start()
                rooms.append(port)
                rooms_names[port] = []

            s.sendto(("Room exist").encode("utf-8"), address)

            data, address = s.recvfrom(255)
            if data.decode() in rooms_names[port]:
                s.sendto(("Nickname used, try again").encode("utf-8"), address)
            else:
                rooms_names[port].append(data.decode())
                s.sendto(("Welcome to the club, buddy!").encode("utf-8"), address)

        except:
            warning = "Something went wrong"
            s.sendto((warning.encode("utf-8")), address)


if __name__ == '__main__':
    main()
