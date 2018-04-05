import random


adminTokens = []
kpTokens = []
superTokens = ['aaa']
userTokens = ['ccc']

users = {}
number_of_users = 0


class Player:
    def __init__(self, chat_id, name='user', type_='user'):
        self.chatID = chat_id
        self.name = name
        self.__type = type_
        self.is_running = False

    def get_type(self):
        return self.__type


class KP(Player):
    def __init__(self, chat_id, name='kp', type_='kp'):
        Player.__init__(self, chat_id, name, type_)
        self.is_free = True
        self.curr_user = None
        self.waiting = []

    def release(self, num):
        if self.curr_user is not None:
            self.curr_user.add_points(num)
            self.curr_user = None
        self.is_free = True
        if len(self.waiting) > 0:
            u = self.waiting.pop(0)
            self.curr_user = u
            self.is_free = False

    def take_user(self, user):
        self.is_free = False
        self.curr_user = user

    def add_user(self, user):
        self.waiting.append(user)


class Admin(Player):
    def __init__(self, chat_id, is_super=False, name='admin', type_='admin'):
        Player.__init__(self, chat_id, name, type_)
        self.is_super = is_super

    def make_super(self):
        self.is_super = True


class User(Player):
    def __init__(self, chat_id, uid,  online_task=0, name='user', type_='user'):
        Player.__init__(self, chat_id, name, type_)
        self.__points = 0
        self.curr_online_task = 0
        self.online_start_task = online_task
        self.online_attempt = 3

        self.uid = uid

        self.curr_off_task = 0

        self.other = []

    def add_points(self, n):
        self.__points += n

    def get_points(self):
        return self.__points

    def set_points(self, points):
        self.__points = points


def gen_token(mode):
    str1 = '1234567890'
    str2 = 'abcdefdhijklmnopqrstuvwxyz'
    str3 = str2.upper()
    str4 = str1 + str2 + str3
    l = list(str4)
    random.shuffle(l)
    token = ''.join([random.choice(l) for x in range(5)])
    if mode == 'admin':
        adminTokens.append(token)
    elif mode == 'kp':
        kpTokens.append(token)
    elif mode == 'super':
        superTokens.append(token)
    return token


def verify_token(token, mode):
    if mode == 'user':
        if userTokens.count(token) > 0:
            userTokens.remove(token)
            return True
    elif mode == 'admin':
        if adminTokens.count(token) > 0:
            adminTokens.remove(token)
            return True
    elif mode == 'kp':
        if kpTokens.count(token) > 0:
            kpTokens.remove(token)
            return True
    elif mode == 'super':
        if superTokens.count(token) > 0:
            superTokens.remove(token)
            return True
    return False
