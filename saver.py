import pickle
import players
import offtxt


def save_users(users):
    file = open('data.sav', 'wb')
    pickle.dump(users, file)
    pickle.dump(players.number_of_users, file)
    pickle.dump(offtxt.locker_kp, file)
    pickle.dump(players.userTokens, file)
    file.close()


def save_mode(mode):
    file = open('mode.sav', 'wb')
    pickle.dump(mode, file)
    file.close()


def load_mode():
    file = open('mode.sav', 'rb')
    try:
        mode = pickle.load(file)
    except EOFError:
        mode = 'online'
    file.close()
    return mode


def load_users():
    file = open('data.sav', 'rb')
    try:
        users = pickle.load(file)
        players.number_of_users = pickle.load(file)
        offtxt.locker_kp = pickle.load(file)
        players.userTokens = pickle.load(file)
    except EOFError:
        users = {}
    file.close()
    return users
