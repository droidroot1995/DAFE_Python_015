import time  # time.time() позволил бы увидеть только непрочитанные сообщения
# from data import db  # здесь можно было бы сохранять сессии (в DataBase(db) добавить accounts & rooms)
from flask import Flask, request, abort  # ... можно было бы реализовать остановку сервера
from datetime import datetime

app = Flask(__name__)
path = []


accounts = {}
rooms = {}


def beauty_time(tm):
    beauty_tm = datetime.fromtimestamp(tm)
    return beauty_tm.strftime('%Y/%m/%d %H:%M')


def get_return(move, ans, new_path=[]):
    move_dict = {'n': 'NEXT', 'b': 'BACK', 'c': 'CHAIN', }
    if len(ans) == 0: ans = 'The list is empty'
    if isinstance(ans, list): ans = ' '.join(ans)
    return {'MOVE': move_dict[move], 'ANS': ans, 'LINK': new_path}


def problem_name(name):
    if not name.isalnum():
        return 'Use only letters and numbers'
    if len(name) < 4:
        return 'The name is too short. It must be longer than 3 characters'
    if len(name) > 32:
        return 'The name is too long. It must be shorter than 33 characters'
    return False


class Account:
    def __init__(self, name):
        self.name = name
        self.time = time.time()

    def add_account(self):
        if problem_name(self.name):
            return get_return('b', problem_name(self.name))

        if self.name in accounts:
            # return get_return('b', f'Name "{self.name}" is already used')  # если добавлять ЛК и пароли
            return get_return('n', f'Welcome to your personal account, "{self.name}"!')

        accounts[self.name] = {
            'groups': {},  # k -> room, v -> nick
            'time_reg': time.time()
        }
        return get_return('n', f'User "{self.name}" was created successfully '
                               f'on {beauty_time(accounts[self.name]["time_reg"])}')


@app.route('/lin')
def lin_0():
    return get_return('c', 'To (log in) / (register), enter your [Name]')


@app.route('/lin/<_acc>', methods=['POST'])
def lin_1(_acc):
    account = Account(_acc)
    return account.add_account()  # status parameters of registration attempt


@app.route('/<_acc>/my')
def my(_acc):
    return get_return('b', [f'Your rooms, "{_acc}":'] + list(accounts[_acc]['groups'].keys()))


@app.route('/<_acc>/all')
def all_rooms(_acc):
    return get_return('b', ['All rooms:'] + list(rooms.keys()))


class Room:
    def __init__(self, acc, room):
        self.acc = acc
        self.room = room
        self.nicks = {}  # k -> account, v -> nick in room
        self.history = {}  # k -> time  v -> (nick, message)

    def add_room(self):
        if problem_name(self.room):
            return get_return('b', problem_name(self.room))
        if self.room in rooms:
            return get_return('b', f'The name "{self.room}" is already taken')
        rooms[self.room] = {'subscribers': self.nicks,
                            'history': self.history,
                            'time_reg': time.time()}

        return get_return('n', f'Room "{self.room}" was created successfully by "{self.acc}" '
                               f"on {beauty_time(rooms[self.room]['time_reg'])}",
                               new_path=[f'/{self.acc}', '/add', ])

    def add_nick(self, nick):

        if problem_name(nick):
            return get_return('b', problem_name(nick))

        if nick in list(rooms[self.room]['subscribers'].values()):
            return get_return('b', f'The nickname "{nick}" is already taken by another user')

        self.nicks[self.acc] = nick
        accounts[self.acc]['groups'][self.room] = nick
        rooms[self.room]['subscribers'][self.acc] = nick

        return get_return('n', f'Participant "{nick}" was was added to the room "{self.room}"')

    def show_history(self):
        ans = ''
        for k in sorted(rooms[self.room]['history']):
            ans += f"{rooms[self.room]['history'][k][0]} ({beauty_time(k)})\n{rooms[self.room]['history'][k][1]}\n\n"
        return ans


@app.route('/<_acc>/add')
def add(_acc):
    # TODO way to create and add room
    return get_return('c', 'To create new room enter its [Name]')


@app.route('/<_acc>/add/<_room>', methods=['POST'])
def add_this(_acc, _room):
    # TODO way to create and add room
    new_room = Room(_acc, _room)
    return new_room.add_room()


@app.route('/<_acc>/enter')  # == subscribe
def come_in(_acc):
    # todo возможна двойная цепь
    # TODO get_name room если не подписан - то придумать ник; ~~указать имя комнаты
    return get_return('c', 'Enter the [Name] of the room you want to go to')


@app.route('/<_acc>/enter/<_room>', methods=['GET', 'POST'])  # Либо в [1], либо в [2]
def try_in_room(_acc, _room):
    if _room not in rooms:
        return get_return('b', 'There is no such room. '
                               'You can find out how to check the list of rooms using /h or /help')
    if _room in accounts[_acc]['groups']:
        return in_room(_acc, _room, accounts[_acc]['groups'][_room])
    else: return get_return('c', f'Enter a nickname - a local [Name] for the room {_room}')


@app.route('/<_acc>/enter/<_room>/<_nick>', methods=['GET', 'POST'])
def in_room(_acc, _room, _nick):
    # TODO show history
    r = Room(_acc, _room)
    print(r.show_history())
    if _room in accounts[_acc]['groups']:  # [0] у пользоватля уже есть ник для комнаты
        return get_return('n', f'\n{_nick}, you entered the room "{_room}"' + r.show_history(),
                          new_path=[f'/{_acc}', '/enter', f'/{_room}', ])
    r = Room(_acc, _room)
    res = r.add_nick(_nick)
    if res['MOVE'] == 'NEXT':  # [1] Если у пользователя нет ника в комнате
        return get_return('n', res['ANS'] + f'\n{_nick}, you entered the room "{_room}"\n' + r.show_history(),
                          new_path=[f'/{_acc}', '/enter', f'/{_room}', ])
    return res


@app.route('/<_acc>/<_room>/send')  # [2]
def send_message(_acc, _room):
    nick = rooms[_room]['subscribers'][_acc]
    # TODO ИЗМЕНИТТЬ ХИСТОРИ
    return get_return('c', f'"{nick}", enter your message.')


@app.route('/<_acc>/<_room>/send/<_mes>', methods=['POST'])
def send_this_message(_acc, _room, _mes):
    nick = rooms[_room]['subscribers'][_acc]
    rooms[_room]['history'][time.time()] = (nick, _mes)
    return get_return('b', f'Message was sent')


app.run()
