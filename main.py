import json
import os

import httpx
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import texts

bot = telebot.TeleBot(os.environ.get('TG_BOT_TOKEN'))


@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    bot.send_message(message.chat.id, texts.start_text, parse_mode="markdown")
    send_menu_message(message)


@bot.message_handler(commands=['task'])
def say_welcome(message):
    send_task_message(message)


@bot.message_handler(commands=['poem'])
def say_welcome(message):
    send_random_poem_message(message)


@bot.message_handler(commands=['menu'])
def say_welcome(message):
    send_menu_message(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    match call.data:
        case 'callback_poem':
            send_random_poem_message(call.message)
        case 'callback_task':
            send_task_message(call.message)
        case 'callback_answer':
            send_answer_message(call.message)
        case 'callback_menu':
            send_menu_message(call.message)
        case _:
            send_menu_message(call.message)


@bot.message_handler(func=lambda message: True)
def check_answer(message):
    result = check(message, message.text.lower())['result']
    if result:
        bot.send_message(message.chat.id, "✅ Correct. Next...\n\n_Правильно. Продолжим..._", parse_mode="markdown")
        send_task_message(message)
    else:
        text = '🙁Wrong. Try again.\n\n_Неверно. Попробуй еще раз, или нажми узнать ответ под сообщением с заданием._'
        bot.send_message(message.chat.id, text, parse_mode="markdown")


def send_menu_message(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton("🔮Learn", callback_data="callback_poem"),
        InlineKeyboardButton("🏋Practice", callback_data="callback_task")
    )
    bot.send_message(message.chat.id, texts.menu_text, parse_mode="markdown", reply_markup=keyboard)


def send_random_poem_message(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton("🔮Next...", callback_data="callback_poem"),
        InlineKeyboardButton("Menu", callback_data="callback_menu")
    )

    poem_text = create_poem_text(get_random_poem(message))
    bot.send_message(message.chat.id, poem_text, parse_mode="markdown", reply_markup=keyboard)


def send_task_message(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton("Answer", callback_data="callback_answer"),
        InlineKeyboardButton("Menu", callback_data="callback_menu")
    )

    task = get_task(message)
    task[task['expected_verb_form']] = '❓'
    task_text = f'{task["first"]} - {task["second"]} - {task["third"]}\n_({task["ru"]})_'
    bot.send_message(message.chat.id, task_text, parse_mode="markdown", reply_markup=keyboard)


def send_answer_message(message):
    answer_text = create_poem_text(get_answer(message))

    bot.send_message(message.chat.id, answer_text, parse_mode="markdown")
    send_task_message(message)


def create_poem_text(poem):
    poem_text = str(poem['poem_template']) \
        .replace('{1}', f'*{poem["first"]}*') \
        .replace('{2}', f'*{poem["second"]}*') \
        .replace('{3}', f'*{poem["third"]}*')
    poem_text = f'{poem_text}\n_({poem["ru"]})_'

    return poem_text


def get_random_poem(message):
    return execute_request(params={
        'user_type': 'tg',
        'user_id': message.chat.id,
        'action': 'poem',
        'user_info': {
            'login': message.chat.username,
            'name': message.chat.first_name
        }
    })


def get_task(message):
    return execute_request(params={
        'user_type': 'tg',
        'user_id': message.chat.id,
        'action': 'task',
        'user_info': {
            'login': message.chat.username,
            'name': message.chat.first_name
        }
    })


def get_answer(message):
    return execute_request(params={
        'user_type': 'tg',
        'user_id': message.chat.id,
        'action': 'answer'
    })


def check(message, answer):
    return execute_request(params={
        'user_type': 'tg',
        'user_id': message.chat.id,
        'action': 'check',
        'answer': answer
    })


def execute_request(params):
    return json.loads(
        httpx.get('https://functions.yandexcloud.net/d4eusbc3q00ksanqgeqi', params=params).text
    )


# For local testing only
if __name__ == '__main__':
    bot.infinity_polling()
