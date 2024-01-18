import datetime
import email
import imaplib
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")


def get_email():
    EMAIL_ACCOUNT = config["Credentials"]["EMAIL_LOGIN"]
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
                data = (f"From: {email_from}\nTo: {email_to}\n"
                        f"Time: {local_message_date}\nSubject: {subject}\n"
                        f"Message: {body.decode('utf-8')}")
                return data

