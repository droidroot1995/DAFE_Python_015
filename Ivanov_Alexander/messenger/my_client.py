import requests
from requests.exceptions import InvalidURL
from json import JSONDecodeError

url = 'http://127.0.0.1:5000'
path = []
for_new_path = []
BASIC_COMMANDS = ['/lin', '/my', '/all', '/add', '/enter', '/send']


def get_hints(link): # необязательно
    # resp = requests.get(link)
    # return resp.request.headers
    pass


def helper():  # необязательно
    print(f'COMMANDS: {get_hints(url)}')  # TODO НЕВЕРНО!!!
    print("You can always enter '/h' or '/help' for help")


def crush_serv():  # необязательно
    print('You crushed the server')
    pass


def stack(resp):
    resp_data = resp.json()
    print(resp_data['ANS'])
    if resp_data['MOVE'] == 'NEXT':  # create new_path
        if resp_data['LINK'] != []:
            path.clear()
            for e in resp_data['LINK']: path.append(e)
        bad_links = ['/lin', '/add', '/enter']
        general = list(set(path) & set(bad_links))[0]
        path.pop(path.index(general))

    elif resp_data['MOVE'] == 'BACK':
        path.pop()  # удаляем некорректное имя и вызываем вновь, если...
        if ([' '] + path)[-1] in BASIC_COMMANDS \
                or ([' ', ' '] + path)[-2] in BASIC_COMMANDS:
            resp = requests.get(url + ''.join(path))
            stack(resp)

    elif resp_data['MOVE'] == 'CHAIN':
        # получить имя, проверить имя, послать на сервер, обработать
        while True:
            text = '[Name]...' if path[-1] != '/send' else '[Text]:'
            name = input(f'($You are here: {"".join(path)})\nEnter a {text}\n').strip()
            if name in ['/b', '/back']:
                path.pop()
                break
            flag, m = is_correct('/' + name, chain=True)
            print(m) if m else 0
            if m == 'CRUSH': crush_serv()
            if flag:
                path.append(f'/{name}')
                resp = requests.post(url + ''.join(path))
                stack(resp)
                break


# для цепочек вызывается проверка с +'/'
def is_correct(com, chain=False):
    if com == '':
        return False, 'The input must contain non-empty characters'
    if com[0] != '/':
        return False, "Command must start with '/'. Try again"
    com = com[chain:]
    if com == '/crush':  # TODO добавить строгость! нельзя пользователю / комнате / нику убить сервер # необязательно
        return False, 'CRUSH'
    if com in ['/b', '/back']:
        if len(path) > 0:
            path.pop()  # безопасно для сервера, т.к в path остается рабочий путь
        return False, ''
    if com in ['/h', '/help']:
        helper()
        return False, ''

    if com.count('/') >= 1:
        if chain: return False, "Name can't have '/'"
        if com.count('/') > 1: return False, "Command can't have more than one '/'"
    return True, ''


while True:
    command = input(f'\n(You are here: {"".join(path)})\nInput your command...\n').strip()
    flag, mes = is_correct(command)
    if flag:
        try:
            path.append(command)
            response = requests.get(url + ''.join(path))
            if response.status_code == 404: raise InvalidURL
            stack(response)

        except InvalidURL as e:
            path.pop(path.index(command)) if command in path else 0
            # print('NP', path)
            print(f'Error InvalidURL: {e}')
            print('Unknown command. Try one of these', end=' ')
            helper()

        except JSONDecodeError as e:
            path.pop(path.index(command)) if command in path else 0
            print(f'Error JSONDecodeError: {e}')
            print(f'Change the command to one of these', end=' ')
            helper()

        except KeyError as e:
            print(f'Error KeyError: {e}')
            print(f'Contact your administrator ...')

        except RecursionError as e:
            print(f'Error RecursionError: {e}')
            print(f'Contact your administrator ...')  # ошибка в коде
        # except ConnectionError as e:
        #     print('The server is temporarily unavailable. Try connecting later')
        except Exception as e:
            print(f'{e} Contact your administrator ...')

    # PSEVDO__CRUH
    elif mes == 'CRUSH':
        crush_serv()
        # break  # Надо отключить сервер, а не клиент
    elif mes: print(mes)
