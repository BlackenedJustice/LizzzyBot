import config
import saver
import players
import logger
import online
import offtxt
import telebot
from telebot import types
from random import randint


bot = telebot.TeleBot(config.token)

tmp_id = 0
mode = 'online'


@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = players.users.get(message.chat.id)
    if user is None or not user.is_running:
        bot.send_message(message.chat.id, '''Привет! Это Лиза. Я вижу, вы решили помочь мне с квестом. Что ж, давайте начинать! 
Я буду присылать вам задания. Решайте их - получите новые. Удачи!
Но сначала, введите код, который был отправлен на почту''')
        bot.register_next_step_handler(message, get_token)
    else:
        bot.send_message(message.chat.id, 'Мы уже познакомились! Продолжай помогать мне:)')
    logger.log_event(message.chat.id, 'Start called', get_user_name(message.chat.id))


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, ''''Вы можете отправить сообщение организатору квеста, напишите и я передам его.
После отправки сообщения квест продолжится, а через некоторое время к вам придет ответ''')
    bot.register_next_step_handler(message, help_user)
    logger.log_event(message.chat.id, 'Help called', get_user_name(message.chat.id))


def help_user(message):
    bot.send_message(config.creatorID, message.text)
    bot.send_message(config.creatorID, 'ID: ' + str(message.chat.id))
    cont(message)


@bot.message_handler(commands=['promote'])
def promote_cmd(message):
    bot.send_message(message.chat.id, config.registration_text, reply_markup=types.ForceReply(selective=False))
    logger.log_event(message.chat.id, 'Promote called')
    bot.register_next_step_handler(message, get_token)


def get_token(message):
    if players.verify_token(message.text, 'user'):
        bot.send_message(message.chat.id, 'Отлично! Теперь давайте знакомиться, скажите название вашей команды')
        bot.register_next_step_handler(message, set_name)
    elif players.verify_token(message.text, 'admin'):
        players.users[message.chat.id] = players.Admin(message.chat.id)
        saver.save_users(players.users)
        bot.send_message(message.chat.id, "Вы успешно повышены до администратора!")
        set_name_cmd(message)
    elif players.verify_token(message.text, 'kp'):
        players.users[message.chat.id] = players.KP(message.chat.id)
        offtxt.locker_kp.append(players.users[message.chat.id])
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
        bot.send_message(message.chat.id, 'Попробуйте еще раз')
        bot.register_next_step_handler(message, get_token)


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
        players.users[id] = players.User(id, players.number_of_users)
        players.number_of_users += 1
        players.users[id].name = message.text
        players.users[id].is_running = True
        saver.save_users(players.users)
        bot.send_message(id, 'Приятно познакомиться, ' + message.text)
        bot.send_message(id, 'Если готовы начать - отправьте любое сообщение!')
        bot.register_next_step_handler(message, online_start)


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
        deleted = players.users.pop(int(words[i + 1]), None)
        bot.send_message(message.chat.id, 'Пользователь успешно удален!')
        logger.log_text('Successful', 'Delete')
        saver.save_users(players.users)


@bot.message_handler(commands=["continue"])
def cont(message):
    if mode == 'online1':  # Исправить!!!
        send_task(message)
    else:
        id = message.chat.id
        user = players.users.get(id)
        if user is None:
            bot.send_message(id, config.unknown_error)
            return
        p = user.check_point
        if p == config.offline_check_points[0]:
            off_start(message)
        elif p == config.offline_check_points[1]:
            book_code(message)
        elif p == config.offline_check_points[2]:
            anti_photo(message)
        elif p == config.offline_check_points[3]:
            traf(message)
        elif p == config.offline_check_points[4]:
            server(message)
        elif p == config.offline_check_points[5]:
            tasks(message)
        elif p == config.offline_check_points[6]:
            final(message)


@bot.message_handler(commands=['reply'])
def reply_cmd(message):
    if message.chat.id != config.creatorID:
        return
    bot.send_message(message.chat.id, "Send id to reply")
    bot.register_next_step_handler(message, reply_id)


def reply_id(message):
    global tmp_id
    tmp_id = message.text
    bot.send_message(message.chat.id, "Enter message")
    bot.register_next_step_handler(message, reply_text)


def reply_text(message):
    bot.send_message(tmp_id, message.text)
    bot.send_message(message.chat.id, "Successful!")


@bot.message_handler(commands=['switch'])
def get_href(message):
    bot.send_message(message.chat.id, 'Введите сслыку на новое видео')
    bot.register_next_step_handler(message, sw_cmd)


def sw_cmd(message):
    config.new_video = message.text
    if message.chat.id != config.creatorID:
        return
    global mode
    if mode == 'online':
        mode = 'offline'
        for u in players.users.values():
            if u.get_type() == 'user':
                msg = bot.send_message(u.chatID, config.new_video + '\nРебят? Вы здесь? Напишите что-нибудь')
                bot.register_next_step_handler(msg, off_start)
            else:
                bot.send_message(u.chatID, 'Квест начался!')
    else:
        mode = 'online'
    bot.send_message(message.chat.id, 'Successful!')
    saver.save_mode(mode)


@bot.message_handler(commands=['showusers'])
def show_users_cmd(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is not None:
        if user.get_type() == 'admin':
            text = 'Users:\n'
            for u in players.users.values():
                if u.get_type() == 'user':
                    text += u.name
                    text += ' - id: '
                    text += str(u.uid)
                    text += ' - online: '
                    text += str(u.curr_online_task)
                    text += '; offline: '
                    text += str(u.curr_off_task)
                    text += '; POINTS = '
                    text += str(u.get_points())
                    text += '\n'
            bot.send_message(id, text)


@bot.message_handler(content_types=['audio'])
def foo(message):
    print(message.audio.file_id)


@bot.message_handler(content_types=['photo'])
def bar(message):
    print(message.photo[0].file_id)


@bot.message_handler(content_types=["text"])
def text_handler(message):
    id = message.chat.id
    print(mode)
    bot.send_message(id, config.unknown_command_error)


def get_user_name(chat_id):
    user = players.users.get(chat_id)
    if user is not None:
        return user.name
    return ''


def online_start(message):
    online.start(message)
    bot.register_next_step_handler(message, check_task)


def send_task(message):
    if mode == 'online':
        online.send_task(message)
        bot.register_next_step_handler(message, check_task)
    else:
        pass  # Оффлайн часть


def check_task(message):
    if message.text == '/help':
        help_cmd(message)
        return
    func = online.check_task(message)
    if func == 'send_task':
        bot.register_next_step_handler(message, send_task)
    elif func == 'check_task':
        bot.register_next_step_handler(message, check_task)


def off_start(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    logger.log_event(user.uid, 'Started', user.name)
    bot.send_message(id, config.offline_geophotos_text)
    bot.send_photo(id, offtxt.geophotos_id[user.uid])
    bot.register_next_step_handler(message, check_start)


def check_start(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    if was_help_cmd(message):
        help_cmd(message)
        return
    l = message.text.split(' ')
    if len(l) > 1:
        bot.send_message(id, config.offline_too_much_words_in_code_error)
        bot.register_next_step_handler(message, check_start)
        return
    code = offtxt.geophotos_codes[user.uid]
    if len(l[0]) != len(code):
        bot.send_message(id, config.offline_mismatch_len_code_error)
        bot.register_next_step_handler(message, check_start)
        return

    if message.text == code:
        bot.send_message(id, config.offline_accepted_geophotos)
        book_code(message)
    else:
        bot.send_message(id, config.offline_wrong_code_error)
        bot.register_next_step_handler(message, check_start)


def book_code(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    user.check_point = config.offline_check_points[1]
    logger.log_event(user.uid, 'Books', user.name)
    saver.save_users(players.users)
    task = offtxt.books_names[user.uid]
    bot.send_message(id, config.offline_books_text1 + task + config.offline_books_text2)
    bot.register_next_step_handler(message, check_books)


def check_books(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    if was_help_cmd(message):
        help_cmd(message)
        return
    l = message.text.split(' ')
    if len(l) > 1:
        bot.send_message(id, config.offline_too_much_words_in_code_error)
        bot.register_next_step_handler(message, check_books)
        return
    ans = offtxt.books_words[user.uid]
    if len(l[0]) != len(ans):
        bot.send_message(id, config.offline_mismatch_len_code_error)
        bot.register_next_step_handler(message, check_books)
        return

    if message.text.lower() == ans.lower():
        bot.send_message(id, config.offline_accepted_books)
        anti_photo(message)
    else:
        bot.send_message(id, config.offline_wrong_code_error)
        bot.register_next_step_handler(message, check_books)


def anti_photo(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    user.check_point = config.offline_check_points[2]
    logger.log_event(user.uid, 'Anti-photo', user.name)
    saver.save_users(players.users)
    a = offtxt.photocross_tasks[user.uid]
    bot.send_message(id, config.offline_photocross_text)
    for i in range(len(a)):
        bot.send_photo(id, offtxt.photocross_id[i])
    bot.register_next_step_handler(message, check_photos)


def check_photos(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    if was_help_cmd(message):
        help_cmd(message)
        return
    ans = offtxt.photocross_code
    a = ans.split(' ')
    l = message.text.split(' ')
    if len(l) > len(a):
        bot.send_message(id, config.offline_too_much_words_error)
        bot.register_next_step_handler(message, check_photos)
        return

    if message.text.lower() == ans.lower():
        bot.send_message(id, config.offline_accepted_photocross)
        code_lock(message)
    else:
        bot.send_message(id, config.offline_wrong_answer_error)
        bot.register_next_step_handler(message, check_photos)


def code_lock(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    text = 'Идите '
    t = ['север', 'к знаниям', ' юг']
    if len(offtxt.locker_kp) == 0:
        bot.send_message(id, config.unknown_error)
    elif offtxt.locker_kp[0].is_free:
        offtxt.locker_kp[0].take_user(user)
        text += t[0]
    elif offtxt.locker_kp[1].is_free:
        offtxt.locker_kp[1].take_user(user)
        text += t[1]
    elif offtxt.locker_kp[2].is_free:
        offtxt.locker_kp[2].take_user(user)
        text += t[2]
    else:
        i = randint(0, 2)
        offtxt.locker_kp[i].add_user(user)
        text += t[i]
    bot.send_message(id, text)
    bot.register_next_step_handler(message, traf)


def traf(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    if message.text == '/continue':
        bot.send_message(id, 'Введите код с трафарета')
        bot.register_next_step_handler(message, traf)
        return
    if was_help_cmd(message):
        help_cmd(message)
        return
    user.check_point = config.offline_check_points[3]
    logger.log_event(user.uid, 'Traf', user.name)
    saver.save_users(players.users)
    code = offtxt.traf_codes[user.uid]
    l = message.text.split(' ')
    if len(l) > 1:
        bot.send_message(id, config.offline_too_much_words_in_code_error)
        bot.register_next_step_handler(message, traf)
        return
    if len(l[0]) != len(code):
        bot.send_message(id, config.offline_mismatch_len_code_error)
        bot.register_next_step_handler(message, traf)
        return

    if message.text == code:
        bot.send_photo(id, offtxt.traf_photo_id, caption='Найдите его...')
        bot.register_next_step_handler(message, server)
    else:
        bot.send_message(id, config.offline_wrong_code_error)
        bot.register_next_step_handler(message, traf)


def server(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    if was_help_cmd(message):
        help_cmd(message)
        return
    user.check_point = config.offline_check_points[4]
    logger.log_event(user.uid, 'Server', user.name)
    saver.save_users(players.users)
    code = offtxt.server_code
    l = message.text.split(' ')
    if len(l) > 1:
        bot.send_message(id, config.offline_too_much_words_in_code_error)
        bot.register_next_step_handler(message, server)
        return
    if len(l[0]) != len(code):
        bot.send_message(id, config.offline_mismatch_len_code_error)
        bot.register_next_step_handler(message, server)
        return

    if message.text == code:
        bot.send_message(id, 'Осталось уже совсем немного...')
        tasks(message)
    else:
        bot.send_message(id, config.offline_wrong_code_error)
        bot.register_next_step_handler(message, server)


def tasks(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    user.check_point = config.offline_check_points[5]
    logger.log_event(user.uid, 'Tasks', user.name)
    saver.save_users(players.users)
    num = user.curr_off_task
    bot.send_message(id, offtxt.final_tasks[num])
    bot.register_next_step_handler(message, check_off_tasks)


def check_off_tasks(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    if was_help_cmd(message):
        help_cmd(message)
        return
    num = user.curr_off_task
    l = message.text.split(' ')
    code = offtxt.final_ans[num]
    if len(l) > 1:
        bot.send_message(id, config.offline_too_much_words_in_code_error)
        bot.register_next_step_handler(message, server)
        return
    if len(l[0]) != len(code):
        bot.send_message(id, config.offline_mismatch_len_code_error)
        bot.register_next_step_handler(message, server)
        return

    if message.text == code:
        user.curr_off_task += 1
        saver.save_users(players.users)
        if user.curr_off_task >= config.offline_num_final_tasks:
            final(message)
        else:
            bot.send_message(id, 'Верный ответ!')
            tasks(message)
    else:
        bot.send_message(id, config.offline_wrong_code_error)
        bot.register_next_step_handler(message, check_off_tasks)


def final(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    user.check_point = config.offline_check_points[6]
    logger.log_event(user.uid, 'Final', user.name)
    saver.save_users(players.users)
    bot.send_message(id, config.offline_final_txt)
    bot.register_next_step_handler(message, check_final)


def check_final(message):
    id = message.chat.id
    user = players.users.get(id)
    if user is None:
        bot.send_message(id, config.unknown_error)
        return
    if was_help_cmd(message):
        help_cmd(message)
        return
    code = offtxt.final_codes[user.uid]
    l = message.text.split(' ')
    if len(l) > 1:
        bot.send_message(id, config.offline_too_much_words_in_code_error)
        bot.register_next_step_handler(message, check_final)
        return
    if len(l[0]) != len(code):
        bot.send_message(id, config.offline_mismatch_len_code_error)
        bot.register_next_step_handler(message, check_final)
        return

    if message.text == code:
        bot.send_message(id, config.offline_win_text)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
        markup.add(types.KeyboardButton('Да'))
        markup.add(types.KeyboardButton('Нет'))
        bot.send_message(id, config.offline_one_more_task, reply_markup=markup)
        bot.register_next_step_handler(message, final_handler)
    else:
        bot.send_message(id, config.offline_wrong_code_error)
        bot.register_next_step_handler(message, check_final)


def final_handler(message):
    u = players.users.get(message.chat.id)
    if message.text == 'Да':
        bot.send_message(message.chat.id, 'Скажите его мне, пожалуйста')
        bot.register_next_step_handler(message, check_inst)
    else:
        bot.send_message(message.chat.id, 'Ну ничего! Я сама найду потом, а пока идите в 646')
        bot.send_message(config.creatorID, u.name + ' - ' + str(u.chatID) + ' END')


def check_inst(message):
    u = players.users.get(message.chat.id)
    if message.text == offtxt.one_more_code:
        bot.send_message(config.creatorID, u.name + ' - ' + str(u.chatID) + ' PRIZE')
        bot.send_message(message.chat.id, 'Супер! Идите в 646, вас там ждет сюрприз)')
    else:
        bot.send_message(message.chat.id, 'Нет, к сожалению он не подошел:( Ну ладно, жду вас в 646!')
        bot.send_message(config.creatorID, u.name + ' - ' + str(u.chatID) + ' END')


def was_help_cmd(message):
    return message.text == '\help'


if __name__ == '__main__':
    #saver.save_users(players.users)
    mode = saver.load_mode()
    players.users = saver.load_users()
    bot.polling(none_stop=True)
