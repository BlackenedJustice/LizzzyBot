import config
import saver
import players
import telebot
from telebot import types


bot = telebot.TeleBot(config.token)
users = {}
is_waiting_for_username = False


@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, '''Привет! Меня зовут Лиза, и меня похители! Я не знаю, где нахожусь! 
Вокруг только голые, облезлые стены и больше ничего... 
Я нашла телефон здесь, в контактах только твой номер. Пожалуйста! Помоги!''')


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, '''Помоги мне... Пожалуйста...''')


@bot.message_handler(commands=['promote'])
def promote_cmd(message):
    bot.send_message(message.chat.id, config.registration_text, reply_markup=types.ForceReply(selective=False))


@bot.message_handler(func=lambda message: message.reply_to_message is not None and
                                          message.reply_to_message.text == config.registration_text)
def get_token(message):
    if players.verify_token(message.text, 'admin'):
        users[message.chat.id] = players.Admin(message.chat.id)
        saver.save_users(users)
        bot.send_message(message.chat.id, "Вы успешно повышены до администратора!")
        set_name_cmd(message)
    elif players.verify_token(message.text, 'kp'):
        users[message.chat.id] = players.KP(message.chat.id)
        saver.save_users(users)
        bot.send_message(message.chat.id, "Вы успешно повышены до КПшника!")
        set_name_cmd(message)
    elif players.verify_token(message.text, 'super'):
        users[message.chat.id] = players.Admin(message.chat.id, is_super=True)
        saver.save_users(users)
        bot.send_message(message.chat.id, "Вы теперь мой царь и бог!")
        set_name_cmd(message)
    else:
        bot.send_message(message.chat.id, config.token_error)


@bot.message_handler(commands=['gentoken'])
def gen_token_cmd(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Супер админ', callback_data='sa'),
               types.InlineKeyboardButton(text='Админ', callback_data='a'),
               types.InlineKeyboardButton(text='КПшник', callback_data='kp'))
    bot.send_message(message.chat.id, 'Выберите нужный вам тип токена:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_query_token(call):
    if call.data == 'sa':
        id = call.message.chat.id
        user = users.get(id)
        if user is not None:
            if user.get_type() == 'admin' and user.is_super:
                token = players.gen_token('super')
                bot.send_message(id, 'Ваш токен: ' + token)
            else:
                bot.send_message(id, config.permission_error)
        else:
            bot.send_message(id, config.registration_error)
    elif call.data == 'a':
        id = call.message.chat.id
        user = users.get(id)
        if user is not None:
            if user.get_type() == 'admin' and user.is_super:
                token = players.gen_token('super')
                bot.send_message(id, 'Ваш токен: ' + token)
            else:
                bot.send_message(id, config.permission_error)
        else:
            bot.send_message(id, config.registration_error)
    elif call.data == 'kp':
        id = call.message.chat.id
        user = users.get(id)
        if user is not None:
            if user.get_type() == 'admin':
                token = players.gen_token('super')
                bot.send_message(id, 'Ваш токен: ' + token)
            else:
                bot.send_message(id, config.permission_error)
        else:
            bot.send_message(id, config.registration_error)


@bot.message_handler(commands=['setname'])
def set_name_cmd(message):
    bot.send_message(message.chat.id, config.set_name_text, reply_markup=types.ForceReply(selective=False))


@bot.message_handler(func=lambda message: message.reply_to_message is not None and
                                          message.reply_to_message.text == config.set_name_text)
def set_name(message):
    id = message.chat.id
    user = users.get(id)
    if user is not None:
        if message.text.find('ChatID:') == -1:
            users[id].name = message.text
            saver.save_users(users)
            bot.send_message(id, 'Приятно познакомиться, ' + message.text)
        else:
            bot.send_message(id, config.set_name_error)
    else:
        bot.send_message(id, config.registration_text)


@bot.message_handler(commands=['deluser'])
def delete_user_cmd(message):
    id = message.chat.id
    user = users.get(id)
    if user is not None:
        if user.get_type() == 'admin' and user.is_super:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
            for u in users.values():
                markup.add(types.KeyboardButton(u.name + ' - ' + u.get_type() + ' ChatID: ' + str(u.chatID)))
            bot.send_message(id, 'Выберите пользователя для удаления:', reply_markup=markup)
            global is_waiting_for_username
            is_waiting_for_username = True
        else:
            bot.send_message(id, config.permission_error)
    else:
        bot.send_message(id, config.registration_error)


@bot.message_handler(content_types=["text"])
def text_handler(message):
    id = message.chat.id
    global is_waiting_for_username
    if is_waiting_for_username:
        words = message.text.split(' ')
        i = 0
        while words[i] != 'ChatID:':
            i += 1
        users.pop(int(words[i + 1]), -1)
        bot.send_message(id, 'Пользователь успешно удален!')
        saver.save_users(users)
        is_waiting_for_username = False
    else:
        bot.send_message(id, config.unknown_command_error)


if __name__ == '__main__':
    users = saver.load_users()
    bot.polling(none_stop=True)