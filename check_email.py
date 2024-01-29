import datetime
import email
import imaplib
import configparser
import html
import html2text

config = configparser.ConfigParser()
config.read("settings.ini")
pause_time = int(config["Credentials"]["pause_time"])


def get_email():
    EMAIL_ACCOUNT = config["Credentials"]["EMAIL_LOGIN"]
    PASSWORD = config["Credentials"]["PASSWORD"]

    mail = imaplib.IMAP4_SSL('mx.inforion.ru')
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.select('inbox')
    result, data = mail.uid('search', None, "ALL")  # (ALL/UNSEEN)
    i = len(data[0].split())

    latest_email_uid = data[0].split()[-1]
    result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    # result, email_data = conn.store(num,'-FLAGS','\\Seen')
    # this might work to set flag to seen, if it doesn't already
    raw_email = email_data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)

    date_tuple = email.utils.parsedate_tz(email_message['Date'])
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
        print(local_date - datetime.timedelta(seconds=pause_time) > datetime.datetime.now())
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
        if local_date - datetime.timedelta(seconds=pause_time) < datetime.datetime.now():

            if email_message.is_multipart():
                for payload in email_message.get_payload():
                    body = payload.get_payload(decode=True).decode('utf-8')
                    data = f"@Gushchin_su @deylo1 @emiev \n{subject}\nMessage: {html2text.html2text(body)}"
                    return data

            else:
                body = email_message.get_payload(decode=True).decode('utf-8')
                data = f"@Gushchin_su @deylo1 @emiev \n{subject}\nMessage: {html2text.html2text(body)}"
                return data
