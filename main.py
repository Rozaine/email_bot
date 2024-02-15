import logging
import time
from datetime import datetime
import telebot
import threading
import configparser

from check_email import get_email
from bd import User

config = configparser.ConfigParser()
config.read("settings.ini")
last_msg_id = 0

User.create_table(User)

tg_token = config["Credentials"]["tg_token"]
admin_id = int(config["Credentials"]["admin_id"])
pause_time = int(config["Credentials"]["pause_time"])
bot = telebot.TeleBot(tg_token)

now = datetime.now().strftime("%d-%m-%Y-%H,%M,%S")
logging.basicConfig(filename=f"logs/log_{now}.log", filemode="w", format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.INFO)


def poling_bot():
    logging.info("Bot start")

    @bot.message_handler(commands=['start'])
    def start_message(message):
        chat_id = message.chat.id
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_add_user = telebot.types.KeyboardButton(text="/add_user")
        button_delete_user = telebot.types.KeyboardButton(text="/delete_user")
        button_get_users_list = telebot.types.KeyboardButton(text="/get_users_list")
        keyboard.add(button_add_user, button_delete_user, button_get_users_list)
        bot.send_message(chat_id, 'Welcome', reply_markup=keyboard)

    @bot.message_handler(commands=["add_user"])
    def get_userid_message(message):
        bot.send_message(message.chat.id, "Enter user_id:")
        bot.register_next_step_handler(message, add_user)
        logging.info("added user")

    @bot.message_handler(commands=['delete_user'])
    def get_userid_message(message):
        users_list = get_users()
        keyboard = telebot.types.InlineKeyboardMarkup()
        for user in users_list:
            keyboard.add(telebot.types.InlineKeyboardButton(text=user, callback_data=f"del_user;{user}"))
        bot.send_message(message.chat.id, "Choose user_id:", reply_markup=keyboard)
        logging.info("deleted user")

    @bot.callback_query_handler(func=lambda call: True)
    def query_handler(call):
        method = str(call.data).split(";")
        if method[0] == 'del_user':
            if call.from_user.id == admin_id:
                delete_user(method[1])
                bot.answer_callback_query(callback_query_id=call.id, text=f'{method[1]} - deleted')
                bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup='')

    @bot.message_handler(commands=['get_users_list'])
    def get_userid_message(message):
        if not get_users():
            bot.send_message(message.chat.id, text="No users")
        else:
            bot.send_message(message.chat.id, text=", ".join(get_users()))

    bot.set_webhook()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)


def add_user(message):
    if message.from_user.id == admin_id:
        try:
            if int(message.text):
                User.create(user_tg_id=message.text)
                bot.send_message(message.chat.id, text=f"{message.text} - user added")
        except ValueError:
            bot.send_message(message.chat.id, text=f"{message.text} - error message type")


def delete_user(user_id):
    delete_user_id = User.get(User.user_tg_id == str(user_id))
    delete_user_id.delete_instance()


def get_users():
    user_list = []
    for user in User.select():
        user_list.append(user.user_tg_id)
    return user_list


def send_emails():
    global last_msg_id
    data = get_email()
    if data is not None and last_msg_id != data:
        for user in User.select():
            try:
                if len(data) > 4096:
                    for x in range(0, len(data), 4096):
                        bot.send_message(user.user_tg_id, data[x:x + 4096])
                        last_msg_id = data
                else:
                    bot.send_message(user.user_tg_id, text=data)
                    last_msg_id = data
                    print(user.user_tg_id)
            except telebot.apihelper.ApiTelegramException as exc:
                logging.exception(exc)
    time.sleep(pause_time)


if __name__ == "__main__":
    try:
        threading.Thread(target=poling_bot).start()
        while True:
            send_emails()
    except:
        logging.exception("stop")
