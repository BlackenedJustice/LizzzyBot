import config
import saver
import players
import logger
import online
import telebot
from telebot import types


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = players.users.get(message.chat.id)
    if user is None or not user.is_running:
        bot.send_message(message.chat.id, '''Привет! Это Лиза. Я вижу, ты решил помочь мне с квестом. Что ж, давай начнём! 
Я буду присылать тебе задания. Решай их - получишь новые. Удачи!
Но сначала, давай познакомимся! Как тебя зовут?''')
        bot.register_next_step_handler(message, set_name)
    else:
        bot.send_message(message.chat.id, 'Мы уже познакомились! Продолжай помогать мне:)')
    logger.log_event(message.chat.id, 'Start called', get_user_name(message.chat.id))


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, '''Помоги мне... Пожалуйста...''')
    logger.log_event(message.chat.id, 'Help called', get_user_name(message.chat.id))


@bot.message_handler(commands=['promote'])
def promote_cmd(message):
    bot.send_message(message.chat.id, config.registration_text, reply_markup=types.ForceReply(selective=False))
    logger.log_event(message.chat.id, 'Promote called')
    bot.register_next_step_handler(message, get_token)


def get_token(message):
    if players.verify_token(message.text, 'admin'):
        players.users[message.chat.id] = players.Admin(message.chat.id)
        saver.save_users(players.users)
        bot.send_message(message.chat.id, "Вы успешно повышены до администратора!")
        set_name_cmd(message)
    elif players.verify_token(message.text, 'kp'):
        players.users[message.chat.id] = players.KP(message.chat.id)
        saver.save_users(players.users)
        bot.send_message(message.chat.id, "Вы успешно повышены до КПшника!")
        set_name_cmd(message)
    elif players.verify_token(message.text, 'super'):
        players.users[message.chat.id] = players.Admin(message.chat.id, is_super=True)
        saver.save_users(players.users)
        bot.send_message(message.chat.id, "Вы теперь мой царь и бог!")
        set_name_cmd(message)
    else:
        logger.log_text('Unsuccessful promotion!', 'Verify_token')
        bot.send_message(message.chat.id, config.token_error)


@bot.message_handler(commands=['gentoken'])
def gen_token_cmd(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Супер админ', callback_data='sa'),
               types.InlineKeyboardButton(text='Админ', callback_data='admin'),
               types.InlineKeyboardButton(text='КПшник', callback_data='kp'))
    bot.send_message(message.chat.id, 'Выберите нужный вам тип токена:', reply_markup=markup)
    logger.log_event(message.chat.id, 'Gen_token called', get_user_name(message.chat.id))


@bot.callback_query_handler(func=lambda call: True)
def handle_query_token(call):
    success = False
    if call.data == 'sa':
        id = call.message.chat.id
        user = players.users.get(id)
        if user is not None:
            if user.get_type() == 'admin' and user.is_super:
                token = players.gen_token('super')
                bot.send_message(id, 'Ваш токен: ' + token)
                success = True
            else:
                bot.send_message(id, config.permission_error)
        else:
            bot.send_message(id, config.registration_error)
    elif call.data == 'admin':
        id = call.message.chat.id
        user = players.users.get(id)
        if user is not None:
            if user.get_type() == 'admin' and user.is_super:
                token = players.gen_token('admin')
                bot.send_message(id, 'Ваш токен: ' + token)
                success = True
            else:
                bot.send_message(id, config.permission_error)
        else:
            bot.send_message(id, config.registration_error)
    elif call.data == 'kp':
        id = call.message.chat.id
        user = players.users.get(id)
        if user is not None:
            if user.get_type() == 'admin':
                token = players.gen_token('kp')
                bot.send_message(id, 'Ваш токен: ' + token)
                success = True
            else:
                bot.send_message(id, config.permission_error)
        else:
            bot.send_message(id, config.registration_error)
    if success:
        logger.log_text('Successful!', 'Gen_token')
    else:
        logger.log_text('Error!', 'Gen_token')


@bot.message_handler(commands=['setname'])
def set_name_cmd(message):
    bot.send_message(message.chat.id, config.set_name_text, reply_markup=types.ForceReply(selective=False))
    bot.register_next_step_handler(message, set_name)


def set_name(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is not None:
        if message.text.find('ChatID:') == -1 and message.text.find('NOPE') == -1:
            logger.log_event(message.chat.id, 'Changed name to "' + message.text + '"', get_user_name(message.chat.id))
            players.users[id].name = message.text
            saver.save_users(players.users)
            bot.send_message(id, 'Приятно познакомиться, ' + message.text)
        else:
            bot.send_message(id, config.set_name_error)
            bot.register_next_step_handler(message, set_name)
    else:
        players.users[id] = players.User(id)
        players.users[id].name = message.text
        players.users[id].is_running = True
        saver.save_users(players.users)
        bot.send_message(id, 'Приятно познакомиться, ' + message.text)
        bot.send_message(id, 'Если готовы начать - отправьте любое сообщение!')
        bot.register_next_step_handler(message, online.start)


@bot.message_handler(commands=['deluser'])
def delete_user_cmd(message):
    id = message.chat.id
    user = players.users.get(id)
    logger.log_event(id, 'Delete user called', get_user_name(id))
    if user is not None:
        if user.get_type() == 'admin' and user.is_super:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
            for u in players.users.values():
                tmp = ''
                if u.get_type() == 'admin' and u.is_super:
                    tmp = ' (super) '
                markup.add(types.KeyboardButton(u.name + ' - ' + tmp + u.get_type() + ' ChatID: ' + str(u.chatID)))
            bot.send_message(id, 'Выберите пользователя для удаления:', reply_markup=markup)
            bot.register_next_step_handler(message, del_user)
        else:
            bot.send_message(id, config.permission_error)
    else:
        bot.send_message(id, config.registration_error)


def del_user(message):
    words = message.text.split(' ')
    i = 0
    if words[0] == 'NOPE':
        return
    while words[i] != 'ChatID:':
        i += 1
    if int(words[i + 1]) >= 0:
        players.users.pop(int(words[i + 1]), -1)
        bot.send_message(message.chat.id, 'Пользователь успешно удален!')
        logger.log_text('Successful', 'Delete')
        saver.save_users(players.users)


@bot.message_handler(commands=["test"])
def test(message):
    bot.register_next_step_handler(message, online.start)


@bot.message_handler(content_types=["text"])
def text_handler(message):
    id = message.chat.id
    bot.send_message(id, config.unknown_command_error)


def get_user_name(chat_id):
    user = players.users.get(chat_id)
    if user is not None:
        return user.name
    return ''


if __name__ == '__main__':
    players.users = saver.load_users()
    bot.polling(none_stop=True)