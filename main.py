import datetime
import email
import imaplib
import time
import telebot
import threading
import configparser

from peewee import SqliteDatabase, Model, AutoField, CharField

config = configparser.ConfigParser()
config.read("settings.ini")


tg_token = config["Credentials"]["tg_token"]
admin_id = int(config["Credentials"]["admin_id"])


bot = telebot.TeleBot(tg_token)

conn = SqliteDatabase('Chinook_Sqlite.sqlite')
cursor = conn.cursor()


def poling_bot():
    bot = telebot.TeleBot(tg_token)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет ✌️ ")

    @bot.message_handler(commands=['add_user'])
    def get_userid_message(message):
        bot.send_message(message.chat.id, "Введите user_id:")
        bot.register_next_step_handler(message, add_user)

    @bot.message_handler(commands=['delete_user'])
    def get_userid_message(message):
        bot.send_message(message.chat.id, "Введите user_id:")
        bot.register_next_step_handler(message, delete_user)

    @bot.message_handler(commands=['get_users'])
    def get_userid_message(message):
        get_users(message)

    bot.infinity_polling()


class BaseModel(Model):
    class Meta:
        database = conn


class User(BaseModel):
    user_id = AutoField(column_name='UserIdDB')
    user_tg_id = CharField(column_name="userTgId")

    class Meta:
        table_name = 'User'


def add_user(message):
    if message.from_user.id == admin_id:
        User.create(user_tg_id=message.text)
        bot.send_message(message.from_user.id, text=f"{message.text} - успешно добавлен")


def delete_user(message):
    if message.from_user.id == admin_id:
        delete_user_id = User.get(User.user_tg_id == message.text)
        delete_user_id.delete_instance()
        bot.send_message(message.from_user.id, text=f"{message.text} - успешно удален")



def get_users(message):
    user_list = []
    for user in User.select():
        user_list.append(user.user_tg_id)
    bot.send_message(message.chat.id, text=str(user_list))


def send_emails():
    EMAIL_ACCOUNT = config["Credentials"]["EMAIL_ACCOUNT"]
    PASSWORD = config["Credentials"]["PASSWORD"]

    mail = imaplib.IMAP4_SSL('outlook.office365.com')
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.list()
    mail.select('inbox')
    result, data = mail.uid('search', None, "UNSEEN")  # (ALL/UNSEEN)
    i = len(data[0].split())

    for x in range(i):
        latest_email_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        # result, email_data = conn.store(num,'-FLAGS','\\Seen')
        # this might work to set flag to seen, if it doesn't already
        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" % (str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                data_list = [email_from, email_to, local_message_date, subject, body.decode('utf-8')]
                for user in User.select():
                    if data_list is not None:
                        User.create_table()
                        print(user.user_tg_id)
                        bot.send_message(user.user_tg_id, text=
                        f"From: {data_list[0]}\nTo: {data_list[1]}\nDate: {data_list[2]}\nSubject: {data_list[3]}\nMsg: {data_list[4]}"
                                         )
    time.sleep(20)


if __name__ == "__main__":
    threading.Thread(target=poling_bot).start()
    while True:
        send_emails()

