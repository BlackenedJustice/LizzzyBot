import config
import telebot
from telebot import types


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, '''Привет! Меня зовут Лиза, и меня похители! Я не знаю, где нахожусь! 
Вокруг только голые, облезлые стены и больше ничего... 
Я нашла телефон здесь, в контактах только твой номер. Пожалуйста! Помоги!''')


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, '''Помоги мне... Пожалуйста...''')


@bot.message_handler(content_types=["text"])
def echo(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)