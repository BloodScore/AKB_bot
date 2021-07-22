import os
import schedule
from threading import Thread
from time import sleep
from telebot import TeleBot, types
from utils import short_url, get_random_anek_page, get_single_anek, get_comments
from dotenv import load_dotenv

load_dotenv()
bot = TeleBot(os.environ.get('BOT_API_KEY'))
users_schedules = {}


@bot.message_handler(commands=['help', 'start'])
def help_command(message):
    bot.send_message(message.chat.id, '/anek - случайный анекдот\n'
                                      '/anek_of_the_day - анекдот раз в день\n'
                                      '/unsubscribe - отписаться от рассылки')


def send_anek(message):
    soup, url = get_random_anek_page()
    url = short_url(url)
    bot.send_message(message.chat.id, get_single_anek(soup))
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data=url)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_yes, key_no)
    bot.send_message(message.chat.id, text='Хотите увидеть топ-3 комментариев?', reply_markup=keyboard)


@bot.message_handler(commands=['anek', 'anek@my_akb_bot'])
def send_random_anek(message):
    send_anek(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'no':
        bot.send_message(call.message.chat.id, '/anek - случайный анекдот\n'
                                               '/anek_of_the_day - анекдот раз в час\n'
                                               '/unsubscribe - отписаться от рассылки')
    else:
        comments = ''
        for comment in get_comments(get_random_anek_page(call.data)[0]):
            comments += comment + '\n\n'
        bot.send_message(call.message.chat.id, comments)


@bot.message_handler(commands=['anek_of_the_day', 'anek_of_the_day@my_akb_bot'])
def send_anek_of_the_day(message):
    if users_schedules.get(message.chat.id):
        bot.send_message(message.chat.id, 'Вы уже подписаны на рассылку')
    else:
        user_schedule = schedule.Scheduler()
        job = user_schedule.every().hour.do(send_anek, message)

        users_schedules[message.chat.id] = [user_schedule, job]

        bot.send_message(message.chat.id, 'Вы подписались на рассылку анекдотов.')

        def schedule_checker():
            while True:
                user_schedule.run_pending()
                sleep(1)

        Thread(target=schedule_checker).start()


@bot.message_handler(commands=['unsubscribe', 'unsubscribe@my_akb_bot'])
def unsubscribe(message):
    if users_schedules.get(message.chat.id):
        users_schedules[message.chat.id][0].cancel_job(users_schedules[message.chat.id][1])
        users_schedules.pop(message.chat.id)
        bot.send_message(message.chat.id, 'Вы отписались от рассылки анекдотов.')
    else:
        bot.send_message(message.chat.id, 'Вы не подписаны на рассылку.')


bot.polling(none_stop=True, interval=0)
