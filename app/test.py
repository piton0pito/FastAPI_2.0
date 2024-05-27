from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from app.config import PASSWORD, USERNAME, HOST, PORT

def send_mail(reception_email: str, code: str):
    # create message object instance
    msg = MIMEMultipart()

    # setup the parameters of the message
    password = PASSWORD
    msg['From'] = USERNAME
    msg['To'] = reception_email
    msg['Subject'] = "Reset password"

    # add in the message body
    msg.attach(MIMEText(code, 'plain'))

    # create server
    server = smtplib.SMTP(f'{HOST}: {PORT}')
    server.starttls()
    server.login(msg['From'], password)
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


