from datetime import datetime, timedelta
import pytz
import configparser
import html2text
from imap_tools import MailBox

config = configparser.ConfigParser()
config.read("settings.ini")
pause_time = int(config["Credentials"]["pause_time"])
login = config["Credentials"]["EMAIL_LOGIN"]
psw = config["Credentials"]["PASSWORD"]
server = config["Credentials"]["MAIL_SERVER"]
utc = pytz.UTC


def get_email():
    with MailBox(server).login(login, psw) as mailbox:
        for msg in mailbox.fetch(reverse=True, mark_seen=False):
            print(msg.date.replace(tzinfo=None) + timedelta(hours=2, minutes=15), datetime.now())
            if msg.date.replace(tzinfo=None) + timedelta(hours=2, minutes=15) >= datetime.now():
                return f"@Gushchin_su @deylo1 @emiev\n{msg.date_str}\n{html2text.html2text(msg.html)}"
            else:
                return None
