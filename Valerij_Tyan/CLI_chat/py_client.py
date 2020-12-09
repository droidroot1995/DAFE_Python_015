import socket
import threading
import time


defect = False
join = False
working = True
connected = False


def receiving(name, sock):
    while not defect:
        try:
            while True:
                data, address = sock.recvfrom(255)
                print(data.decode("utf-8"))
                time.sleep(0.5)
        except:
            pass


host = socket.gethostbyname(socket.gethostname())
port = 0

server = (host, 9089)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

while working == True:
    defect = False
    join = False

    while connected == False:
        try:
            port = input("Create room with number or write number of room to connect to it: ")
            if port == "/quit":
                s.close()
                working = False
                break

            s.sendto((port).encode("utf-8"), server)
            port = int(port)
            time.sleep(0.1)
            data, address = s.recvfrom(255)
            if data.decode("utf-8") != "Room exist":
                print("Room problem\nTry another one")
                continue
            print(data.decode("utf-8"))
            user = input("Представься, мразь!")
            s.sendto(user.encode("utf-8"), server)
            time.sleep(0.1)
            data, address = s.recvfrom(255)
            print(data.decode("utf-8"))
            if data.decode("utf-8") == "Welcome to the club, buddy!":
                connected = True
        except:
            print("Something went wrong")

    room = (host, 9090 + port)

    room_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    room_s.bind((host, 0))
    room_s.setblocking(0)

    rT = threading.Thread(target=receiving, args=("RecvThread", room_s))
    rT.start()

    while defect == False:

        if join == False:

            room_s.sendto(("[" + user + "] -> joined to server ").encode("utf-8"), room)
            join = True
        else:
            try:
                message = input()

                if message == "/change_room":
                    room_s.sendto(("[" + user + "] <- left chat").encode("utf-8"), room)
                    connected = False
                    defect = True

                if message == "/quit":
                    room_s.sendto(("[" + user + "] <- left server ").encode("utf-8"), room)
                    defect = True
                    working = False

                if message != "":
                    room_s.sendto(("[" + user + "]::" + message).encode("utf-8"), room)

                time.sleep(0.2)
            except:
                room_s.sendto(("[" + user + "] <- left server").encode("utf-8"), room)
                defect = True
    rT.join()
s.close()

if __name__ == '__main__':
    print()
