import players
import text
import telebot
import time
import config
import logger
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
    bot.register_next_step_handler(message, check_task)


def check_task(message):
    user = players.users.get(message.chat.id)
    if check_task_format(user.curr_online_task):
        if message.text == text.ans[user.curr_online_task]:
            user.curr_online_task += 1
            user.curr_online_task %= len(text.task)
            if user.curr_online_task == user.online_start_task:
                bot.send_message(message.text.id, config.online_task_ending)
                pass
            else:
                bot.send_message(message.chat.id, config.online_task_accepted)
                send_text(message.chat, user.curr_online_task)
                bot.register_next_step_handler(message, send_text)
        else:
            user.online_attempt -= 1
            if user.online_attempt > 0:
                bot.send_message(message.chat.id, config.online_task_wrong_answer + str(user.online_attempt))
                bot.register_next_step_handler(message, check_task)
            else:
                bot.send_message(message.chat.id, config.online_task_end_of_attempts)
                bot.register_next_step_handler(message, send_task)
    else:
        bot.send_message(message.chat.id, config.online_task_wrong_format)
        bot.register_next_step_handler(message, check_task)


def check_task_format(num):
    return True
