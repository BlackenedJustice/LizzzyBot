import pickle

def save_users(users):
    file = open('data.sav', 'wb')
    pickle.dump(users, file)
    file.close()


def load_users():
    file = open('data.sav', 'rb')
    try:
        users = pickle.load(file)
    except EOFError:
        users = {}
    file.close()
    return users
