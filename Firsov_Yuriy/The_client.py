import threading, time, socket

Stop = False
join = False
Continue = True
Connected = False


def receiving(name, sock):
    while not Stop:
        try:
            while True:
                data, addr = sock.recvfrom(255)
                print(data.decode("utf-8"))
                time.sleep(0.2)
        except:
            pass


host = socket.gethostbyname(socket.gethostname())
port = 0

server = (host, 9089)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

while Continue == True:
    Stop = False
    join = False

    while Connected == False:
        try:
            port = input("Write number of room: ")
            if port == "s":
                s.close()
                Continue = False
                break

            s.sendto((port).encode("utf-8"), server)
            port = int(port)
            time.sleep(0.1)
            data, addr = s.recvfrom(255)
            if data.decode("utf-8") != "Room exist":
                print("Room problem\nTry another one")
                continue
            print(data.decode("utf-8"))
            alias = input("Name: ")
            s.sendto(alias.encode("utf-8"), server)
            time.sleep(0.1)
            data, addr = s.recvfrom(255)
            print(data.decode("utf-8"))
            if data.decode("utf-8") == "Connected":
                Connected = True
        except:
            print("Something went wrong")

    room = (host, 9090 + port)

    room_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    room_s.bind((host, 0))
    room_s.setblocking(0)

    rT = threading.Thread(target=receiving, args=("RecvThread", room_s))
    rT.start()

    while Stop == False:

        if join == False:

            room_s.sendto(("[" + alias + "] => join chat ").encode("utf-8"), room)
            join = True
        else:
            try:
                chat = input()

                if chat == "q":
                    room_s.sendto(("[" + alias + "] <= left chat").encode("utf-8"), room)
                    Connected = False
                    Stop = True

                if chat == "s":
                    room_s.sendto(("[" + alias + "] <= left chat").encode("utf-8"), room)
                    Stop = True
                    Continue = False

                if chat != "":
                    room_s.sendto(("[" + alias + "]::" + chat).encode("utf-8"), room)

                time.sleep(0.2)
            except:
                room_s.sendto(("[" + alias + "] <= left chat").encode("utf-8"), room)
                Stop = True
    rT.join()
s.close()
