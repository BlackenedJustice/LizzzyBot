import players
import text
import config
import logger
import saver
from bot import bot


def start(message):
    id = message.chat.id
    bot.send_message(id, 'Начинаем!')
    user = players.users[id]
    if user is None:
        bot.send_message(message.chat.id, config.unknown_error)
        return
    logger.log_event(id, "Start called", user.name)
    if type(user) is players.User:
        send_task(message)


def send_text(user_id, n_from, cnt=1):
    if n_from >= len(text.messages):
        return
    for i in range(cnt):
        bot.send_message(user_id, text.messages[n_from + i])


def send_task(message):
    user = players.users.get(message.chat.id)
    num = user.curr_online_task
    if text.t_format[num] == 'txt':
        bot.send_message(message.chat.id, text.task[num])
    elif text.t_format[num] == 'pic':
        bot.send_photo(message.chat.id, text.pic_id, caption=text.task[num])
    elif text.t_format[num] == 'audio':
        bot.send_audio(message.chat.id, text.audio_id, caption=text.task[num])


def check_task(message):
    user = players.users.get(message.chat.id)
    func = 'nope'
    if check_task_format(user.curr_online_task, message.text):
        if message.text.lower() == text.ans[user.curr_online_task]:
            prev_task = user.curr_online_task
            reset_user_attempts(user)
            user.add_points(config.points_for_task)
            if user.curr_online_task == user.online_start_task:
                bot.send_message(message.chat.id, config.online_task_ending)
                pass  # Здесь будет переход к оффлайн части квеста
            else:
                bot.send_message(message.chat.id, config.online_task_accepted)
                send_text(message.chat.id, prev_task)
                func = 'send_task'
        else:
            user.online_attempt -= 1
            if user.online_attempt > 0:
                bot.send_message(message.chat.id, config.online_task_wrong_answer + str(user.online_attempt))
                func = 'check_task'
            else:
                prev_task = user.curr_online_task
                reset_user_attempts(user)
                bot.send_message(message.chat.id, config.online_task_end_of_attempts)
                send_text(message.chat.id, prev_task)
                func = 'send_task'
        saver.save_users(players.users)
    else:
        bot.send_message(message.chat.id, config.online_task_wrong_format)
        func = 'check_task'
    return func


def reset_user_attempts(user):
    user.curr_online_task += 1
    user.curr_online_task %= len(text.task)
    user.online_attempt = config.online_attempts


def check_task_format(num, txt):
    a = txt.split(' ')
    b = text.ans[num].split(' ')
    return len(a) == len(b)
