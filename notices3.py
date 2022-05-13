# Импорт необходимых библиотек
import telebot
import time
from telebot.apihelper import ApiTelegramException
from config import *
from flask import Flask, request
import logging
import os
import emoji

# Переменные
bot = telebot.TeleBot(BOT_TOKEN)
chat_id = 0
user_id = 0
user_id2 = 0
user_id3 = 0
user_id4 = 0
user_id5 = 0
turn = True
bot_message = 'Проверка'


@bot.message_handler(commands=['start'])
def start(message):
    # Начало работы бота (выбор того, что делать с аккаунтом пользователя)
    keyboard = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(text='Проверять' + emoji.emojize(':magnifying_glass_tilted_left:'),
                                                callback_data='Проверять' + emoji.emojize('magnifying_glass_tilted_left'))
    keyboard.add(button)
    button = telebot.types.InlineKeyboardButton(text='Отправлять уведомления' + emoji.emojize(':bell:'),
                                                callback_data='Отправлять уведомления' + emoji.emojize(':bell:'))
    keyboard.add(button)
    bot.send_message(message.chat.id, text='\nНа аккаунт, с которого вы пишите нужно будет присылать уведомление о сносе'
                                           'группы/аккаунта или этот аккаунт нужно проверять на то, '
                                           'заблокирован ли он? '
                                           '\nЕсли бот уже активен, то вы можете использовать следующие команды:'
                                           '\n/turnup - если хотите, чтобы был включен звук '
                                           '\n/turnoff - если хотите, чтобы сообщение приходило без звука. '
                                           '\n/change - чтобы изменить проверочное сообщение бота',
                     reply_markup=keyboard)


@bot.message_handler(commands=['turnup'])
def turnup(message):
    global turn
    turn = True
    bot.send_message(message.chat.id, 'Теперь подписчикам не приходит звук сообщения.' +
                     emoji.emojize(':bell_with_slash:'))


@bot.message_handler(commands=['turnoff'])
def turnoff(message):
    global turn
    turn = False
    bot.send_message(message.chat.id, 'Теперь сообщение бота имеет звуковое уведомление.' + emoji.emojize(':bell:'))


@bot.message_handler(commands=['change'])
def change(message):
    bot.send_message(message.chat.id, 'Напишите фразу, которую хотите видеть в проверочном сообщении бота.')
    bot.register_next_step_handler(message, change_2)


def change_2(message):
    global bot_message
    bot_message = message.text
    bot.send_message(message.chat.id, 'Теперь проверочное сообщение будет "{}"'.format(bot_message))


@bot.callback_query_handler(func=lambda call: True)  # Если пользователь нажал на кнопку на клавиатуре
def callback_worker(call):
    # Глобальные переменные
    global user_id
    global chat_id
    bot.delete_message(call.message.chat.id, call.message.message_id)  # Удаление сообщения с клавиатурой для удобства

    if call.data == 'Отправлять уведомления' + emoji.emojize(':bell:'):
        chat_id = call.message.chat.id  # Сохранение id пользователя, которому нужно будет отправлять уведомления
        bot.send_message(call.message.chat.id,
                         'Хорошо, id сохранён. Надо будет проверять что-либо ещё? (Напишите id группы/Нет)')
        bot.register_next_step_handler(call.message, step_3)

    else:  # Если пользователь нажимает на кнопку "Проверять"
        user_id = call.message.chat.id  # Сохранение id пользователя, которого надо будет проверять
        bot.send_message(call.message.chat.id, 'Хорошо, проверка запущена.' + emoji.emojize(':check_mark_button:'))
        while True:
            time.sleep(10)  # Бот проверяет пользователя каждые 5 секунд
            try:
                chat_message = bot.send_message(user_id, bot_message, disable_notification=turn)
                bot.delete_message(user_id, chat_message.id)  # удаление сообщения для того, чтобы не засорять чат

            except ApiTelegramException:  # Если аккаунт/группа удалён
                bot.send_message(chat_id, 'Бот оповещает о том, что аккаунт удален.' + emoji.emojize(':cross_mark:'))
                break


def step_3(message):  # Функция для того, чтобы проверять ответ пользователя
    global user_id2

    if message.text in ['Нет', 'нет']:  # Если пользователь отвечает 'Нет'
        bot.send_message(message.chat.id, 'Хорошо. Теперь, если вы еще не написали боту с аккаунта, '
                                          'который надо будет проверять, то напишите и запустится проверка.'
                         + emoji.emojize(':check_mark_button:'))

    else:
        user_id2 = int(message.text)  # Сохранение id группы
        bot.send_message(message.chat.id, 'Id сохранён.' + emoji.emojize(':check_mark_button:') + '(1 группа) \n'
                                          'Надо будет проверять что-либо ещё? (Напишите id группы/Нет)')
        bot.register_next_step_handler(message, step_4)


def step_4(message):
    global user_id3
    global user_id2

    if message.text in ['Нет', 'нет']:  # Если пользователь отвечает 'Нет'
        bot.send_message(message.chat.id, 'Хорошо. Проверка запущена.')
        while True:
            time.sleep(10)  # Бот проверяет чат каждые 60 секунд
            try:  # Работа проверки ботом
                if user_id2:
                    chat_message = bot.send_message(user_id2, bot_message, disable_notification=turn)
                    bot.delete_message(user_id2, chat_message.id)

            except ApiTelegramException:
                bot.send_message(chat_id, 'Бот оповещает о том, что группа 1 удалена. Либо бот не находится в группе.'
                                 + emoji.emojize(':cross_mark:'))
                break
    else:
        user_id3 = int(message.text)  # Сохранение id группы
        bot.send_message(message.chat.id, 'Id сохранён.' + emoji.emojize(':check_mark_button:') + '(2 группа) \n'
                                          'Надо будет проверять что-либо ещё? (Напишите id группы/Нет)')
        bot.register_next_step_handler(message, step_5)


def step_5(message):
    global user_id4
    global user_id2
    global user_id3

    if message.text in ['Нет', 'нет']:  # Если пользователь отвечает 'Нет'
        bot.send_message(message.chat.id, 'Хорошо. Проверка запущена.')
        while True:
            time.sleep(10)  # Бот проверяет чат каждые 60 секунд
            try:  # Работа проверки ботом
                if user_id2:
                    chat_message = bot.send_message(user_id2, bot_message, disable_notification=turn)
                    bot.delete_message(user_id2, chat_message.id)

                time.sleep(5)
                if user_id3:
                    chat_message = bot.send_message(user_id3, bot_message, disable_notification=turn)
                    bot.delete_message(user_id3, chat_message.id)

            except ApiTelegramException:
                if user_id2:
                    bot.send_message(chat_id, 'Бот оповещает о том, что группа 1 удалена. '
                                              'Либо бот не находится в группе.' + emoji.emojize(':cross_mark:'))
                    user_id2 = 0
                else:
                    bot.send_message(chat_id, 'Бот оповещает о том, что группа 2 удалена. '
                                              'Либо бот не находится в группе.' + emoji.emojize(':cross_mark:'))
                    user_id3 = 0

                if user_id2 == 0 and user_id3 == 0:
                    break
    else:
        user_id4 = int(message.text)  # Сохранение id группы
        bot.send_message(message.chat.id, 'Id сохранён.' + emoji.emojize(':check_mark_button:') + '(3 группа) \n'
                                          'Надо будет проверять что-либо ещё? (Напишите id группы/Нет)')
    bot.register_next_step_handler(message, step_6)


def step_6(message):
    global user_id5
    global user_id2
    global user_id3
    global user_id4

    if message.text in ['Нет', 'нет']:  # Если пользователь отвечает 'Нет'
        bot.send_message(message.chat.id, 'Хорошо. Проверка запущена.')
        while True:
            time.sleep(10)  # Бот проверяет чат каждые 60 секунд
            try:  # Работа проверки ботом
                if user_id2:
                    num = 1
                    chat_message = bot.send_message(user_id2, bot_message, disable_notification=turn)
                    bot.delete_message(user_id2, chat_message.id)

                time.sleep(5)
                if user_id3:
                    num = 2
                    chat_message = bot.send_message(user_id3, bot_message, disable_notification=turn)
                    bot.delete_message(user_id3, chat_message.id)

                time.sleep(5)
                if user_id4:
                    num = 3
                    chat_message = bot.send_message(user_id4, bot_message, disable_notification=turn)
                    bot.delete_message(user_id4, chat_message.id)

            except ApiTelegramException:
                if num == 1:
                    bot.send_message(chat_id, 'Бот оповещает о том, что группа 1 удалена. '
                                              'Либо бот не находится в группе.' + emoji.emojize(':cross_mark:'))
                    user_id2 = 0

                if num == 2:
                    bot.send_message(chat_id, 'Бот оповещает о том, что группа 2 удалена. '
                                              'Либо бот не находится в группе.' + emoji.emojize(':cross_mark:'))
                    user_id3 = 0

                elif num == 3:
                    bot.send_message(chat_id, 'Бот оповещает о том, что группа 3 удалена. '
                                              'Либо бот не находится в группе.' + emoji.emojize(':cross_mark:'))
                    user_id4 = 0

                if user_id2 == 0 and user_id3 == 0 and user_id4 == 0:
                    break

    else:
        user_id5 = int(message.text)  # Сохранение id группы
        bot.send_message(message.chat.id, 'Id сохранён.' + emoji.emojize(':check_mark_button:')
                         + '(4 группа) \nПроверка запущена.')
        while True:
            time.sleep(10)  # Бот проверяет чат каждые 60 секунд
            try:  # Работа проверки ботом
                if user_id2:
                    num = 1
                    chat_message = bot.send_message(user_id2, bot_message, disable_notification=turn)
                    bot.delete_message(user_id2, chat_message.id)

                time.sleep(5)
                if user_id3:
                    num = 2
                    chat_message = bot.send_message(user_id3, bot_message, disable_notification=turn)
                    bot.delete_message(user_id3, chat_message.id)

                time.sleep(5)
                if user_id4:
                    num = 3
                    chat_message = bot.send_message(user_id4, bot_message, disable_notification=turn)
                    bot.delete_message(user_id4, chat_message.id)

                time.sleep(5)
                if user_id5:
                    num = 4
                    chat_message = bot.send_message(user_id5, bot_message, disable_notification=turn)
                    bot.delete_message(user_id5, chat_message.id)

            except ApiTelegramException:
                if num == 1:
                    bot.send_message(chat_id,
                                     'Бот оповещает о том, что группа 1 удалена. Либо бот не находится в группе.'
                                     + emoji.emojize(':cross_mark:'))
                    user_id2 = 0

                if num == 2:
                    bot.send_message(chat_id,
                                     'Бот оповещает о том, что группа 2 удалена. Либо бот не находится в группе.'
                                     + emoji.emojize(':cross_mark:'))
                    user_id3 = 0

                elif num == 3:
                    bot.send_message(chat_id,
                                     'Бот оповещает о том, что группа 3 удалена. Либо бот не находится в группе.'
                                     + emoji.emojize(':cross_mark:'))
                    user_id4 = 0

                elif num == 4:
                    bot.send_message(chat_id,
                                     'Бот оповещает о том, что группа 4 удалена. Либо бот не находится в группе.'
                                     + emoji.emojize(':cross_mark:'))
                    user_id5 = 0

                if user_id2 == 0 and user_id3 == 0 and user_id4 == 0 and user_id5 == 0:
                    break


if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)


    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(
            url=APP_URL)
        return "?", 200


    server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))

else:
    bot.remove_webhook()
    if __name__ == '__main__':
        bot.polling(none_stop=True)
