import os
import smtplib
import utils
from email.message import EmailMessage


def send_email(to, content, status=0):
    try:
        msg = EmailMessage()
        msg.set_content(content)

        msg['Subject'] = "Export is successful" if status == 1 else "Export error"
        msg['From'] = os.environ["GMAIL_EMAIL"]
        msg['To'] = to

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.environ["GMAIL_EMAIL"], os.environ["GMAIL_PASS"])
        server.send_message(msg)
        server.quit()

    except Exception as e:
        utils.save_to_log(f"Failed to send an email: {e}")
