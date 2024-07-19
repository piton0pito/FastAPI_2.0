import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel

load_dotenv()

HOST = os.environ.get("MAIL_HOST")
USERNAME = os.environ.get("MAIL_USERNAME")
PASSWORD = os.environ.get("MAIL_PASSWORD")
PORT = os.environ.get("MAIL_PORT", 465)
# https://ethereal.email/create

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

PASS_ADMIN = os.environ.get("PASS_ADMIN")
EMAIL_ADMIN = os.environ.get("EMAIL_ADMIN")

TEST_USER_EMAIL = os.environ.get("TEST_USER_EMAIL")
TEST_USER_PHONE = os.environ.get("TEST_USER_PHONE")
TEST_USER_FIRST_NAME = os.environ.get("TEST_USER_FIRST_NAME")
TEST_USER_LAST_NAME = os.environ.get("TEST_USER_LAST_NAME")
TEST_USER_SURNAME = os.environ.get("TEST_USER_SURNAME")
TEST_USER_LICENSE = os.environ.get("TEST_USER_LICENSE")
TEST_USER_PASSWORD = os.environ.get("TEST_USER_PASSWORD")
