import smtplib
from email.mime.text import MIMEText
from email.header import Header
from random import randint
from fastapi import Depends

from fastapi import HTTPException
from datetime import datetime, timedelta

from fastapi import Response
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, encode, decode
from hashlib import sha256
from sqlmodel import select, Session

from app.db import get_session
from app.models import User

SECRET_KEY = "vorona govorit CAR"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


credentials_error = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)

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


def send_mail(reception_email, text):
    login = ''
    password = ''

    msg = MIMEText(text, 'plain', 'utf-8')
    msg['Subject'] = Header('Reset password', 'utf-8')
    msg['From'] = login
    msg['To'] = reception_email

    s = smtplib.SMTP('smtp.yandex.ru', 587, timeout=10)
    try:
        s.starttls()
        s.login(login, password)
        s.sendmail(msg['From'], reception_email, msg.as_string())
    except:
        raise HTTPException(status_code=500, detail='Internal Server Error')
    finally:
        s.quit()
    raise HTTPException(status_code=200)


def gen_res_key():
    num = str(randint(1, 999999))
    return ('0' * (6-len(num))) + num

def get_delta_time(date_1: datetime, date_2: datetime):
    time_difference = date_2 - date_1
    minutes_difference = time_difference.seconds / 60 + time_difference.microseconds / 1000000 / 60
    return int(minutes_difference)