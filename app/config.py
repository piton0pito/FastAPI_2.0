import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel

load_dotenv()

HOST = os.environ.get("MAIL_HOST")
USERNAME = os.environ.get("MAIL_USERNAME")
PASSWORD = os.environ.get("MAIL_PASSWORD")
PORT = os.environ.get("MAIL_PORT", 465)
#https://ethereal.email/create

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

PASS_ADMIN = os.environ.get("PASS_ADMIN")
EMAIL_ADMIN = os.environ.get("EMAIL_ADMIN")