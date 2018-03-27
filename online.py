import players
import text
import telebot
import time
import config
import logger
import saver
from bot import bot
from random import randint


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
    for i in range(cnt):
        bot.send_message(user_id, text.messages[n_from + i])
        time.sleep(randint(1, 3))


def send_task(message):
    user = players.users.get(message.chat.id)
    bot.send_message(message.chat.id, text.task[user.curr_online_task])


def check_task(message):
    user = players.users.get(message.chat.id)
    func = 'nope'
    if check_task_format(user.curr_online_task):
        if message.text == text.ans[user.curr_online_task]:
            prev_task = user.curr_online_task
            reset_user_attempts(user)
            if user.curr_online_task == user.online_start_task:
                bot.send_message(message.chat.id, config.online_task_ending)
                bot.send_message(message.chat.id, "Done! Repeat!")
                func = 'send_task'
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


def check_task_format(num):
    return True
