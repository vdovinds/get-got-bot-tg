import json
import os
import telebot
import texts
import httpx

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(os.environ.get('TG_BOT_TOKEN'))


@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    bot.send_message(message.chat.id, texts.start_text, parse_mode="markdown")
    send_menu_message(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    match call.data:
        case 'callback_poem':
            send_random_poem_message(call.message)
        case 'callback_task':
            bot.send_message(call.message.chat.id, "задание", parse_mode="markdown")
        case 'callback_menu':
            send_menu_message(call.message)
        case _:
            send_menu_message(call.message)


def send_menu_message(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton("🔮Учить стих", callback_data="callback_poem"),
        InlineKeyboardButton("🏋Тренировать", callback_data="callback_task")
    )
    bot.send_message(message.chat.id, texts.menu_text, parse_mode="markdown", reply_markup=keyboard)


def send_random_poem_message(message):
    poem = get_random_poem(message)
    poem_text = str(poem['poem_template'])\
        .replace('{1}', f'*{poem["first"]}*')\
        .replace('{2}', f'*{poem["second"]}*')\
        .replace('{3}', f'*{poem["third"]}*')
    poem_text = f'{poem_text}\n_({poem["ru"]})_'

    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton("🔮Еще...", callback_data="callback_poem"),
        InlineKeyboardButton("Меню", callback_data="callback_menu")
    )

    bot.send_message(message.chat.id, poem_text, parse_mode="markdown", reply_markup=keyboard)


def get_random_poem(message):
    params = {
        'user_type': 'tg',
        'user_id': message.chat.id,
        'action': 'poem'
    }

    return json.loads(
        httpx.get('https://functions.yandexcloud.net/d4eusbc3q00ksanqgeqi', params=params).text
    )


# For local testing only
if __name__ == '__main__':
    bot.infinity_polling()
