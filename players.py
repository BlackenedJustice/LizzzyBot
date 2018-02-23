class Player:
    def __init__(self, chat_id, name='user', type_='user'):
        self.chatID = chat_id
        self.name = name
        self.__type = type_

    def get_type(self):
        return self.__type


class KP(Player):
    pass


class Admin(Player):
    def __init__(self, chat_id, is_super=False, name='admin', type_='admin'):
        Player.__init__(self, chat_id, name, type_)
        self.is_super = is_super

    def make_super(self):
        self.is_super = True


class User(Player):
    def __init__(self, chat_id, name='user', type_='user'):
        Player.__init__(self, chat_id, name, type_)
        self.points = 0
