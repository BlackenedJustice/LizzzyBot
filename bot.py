import config
import saver
import players
import telebot
from telebot import types


bot = telebot.TeleBot(config.token)
users = {}


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
    elif players.verify_token(message.text, 'kp'):
        users[message.chat.id] = players.KP(message.chat.id)
        saver.save_users(users)
        bot.send_message(message.chat.id, "Вы успешно повышены до КПшника!")
    elif players.verify_token(message.text, 'super'):
        users[message.chat.id] = players.Admin(message.chat.id, is_super=True)
        saver.save_users(users)
        bot.send_message(message.chat.id, "Вы теперь мой царь и бог!")
    else:
        bot.send_message(message.chat.id, config.token_error)


@bot.message_handler(commands=['gentoken'])
def gen_token_cmd(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Супер админ', callback_data='sa'),
               types.InlineKeyboardButton(text='Админ', callback_data='a'),
               types.InlineKeyboardButton(text='КПшник', callback_data='kp'))
    bot.send_message(message.chat.id, 'Выберите тип токена:', reply_markup=markup)


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


@bot.message_handler(content_types=["text"])
def echo(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    users = saver.load_users()
    #users[config.creatorID] = players.Admin(config.creatorID, True, 'Yury')
    bot.polling(none_stop=True)