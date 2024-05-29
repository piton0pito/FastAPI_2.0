import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import openpyxl

from app.config import HOST, USERNAME, PASSWORD, PORT
from openpyxl import Workbook

from random import randint
from fastapi import Depends

from fastapi import HTTPException
from datetime import datetime, timedelta

from app.config import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, encode, decode
from hashlib import sha256
from sqlmodel import select, Session

from app.db import get_session
from app.models import User

# SECRET_KEY = "vorona_govorit_CAR"
# ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_error = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}, )


def create_access_token(data: dict, exp: timedelta = None):
    to_encode = data.copy()
    if exp:
        expire = datetime.utcnow() + exp
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_error
        user = session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise credentials_error
        return user
    except PyJWTError:
        raise credentials_error


def hash_password(password: str):
    return sha256(password.encode()).hexdigest()


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
    raise HTTPException(status_code=200)


def gen_res_key():
    num = str(randint(1, 999999))
    return ('0' * (6 - len(num))) + num


def get_delta_time(date_1: datetime, date_2: datetime):
    time_difference = date_2 - date_1
    minutes_difference = time_difference.seconds / 60 + time_difference.microseconds / 1000000 / 60
    return int(minutes_difference)


def get_xlsx(users, file_name):
    # Create a workbook and select the active sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    # Write the headers
    headers = ['id', 'hash_password', 'surname', 'date_reg', 'email', 'role', 'first_name', 'last_name', 'license']
    sheet.append(headers)
    # Write the users
    for user in users:
        user = dict(user)
        row = [user[header] for header in headers]
        sheet.append(row)
    # Save the workbook
    workbook.save(file_name)

