from fastapi import FastAPI
from fastapi.security import HTTPBasic
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, select

from app.config import EMAIL_ADMIN, PASS_ADMIN
from app.db import get_session

from app.main import app
from app.models import User

client = TestClient(app)

engine = create_engine("sqlite:///./test_data_base.db")
security = HTTPBasic()


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
SQLModel.metadata.create_all(engine)


def test_418():
    response = client.get("/mem")
    assert response.status_code == 418


def test_user_create_first_admin():
    response = client.post("/admin/create_first_admin")
    assert response.status_code == 201


def test_user_register_success():
    data = {
        "email": "test_email@mail.ru",
        "phone": "+78005553535",
        "first_name": "Имя",
        "last_name": "Отчество",
        "surname": "Фамилия",
        "license": "0123456789",
        "password": "test",
        "complete_password": "test"
    }
    response = client.post("/register/", json=data)
    assert response.status_code == 201


def test_user_register_invalid_email():
    data = {
        "email": "test_email@mail.ru",
        "phone": "+78005553535",
        "first_name": "Имя",
        "last_name": "Отчество",
        "surname": "Фамилия",
        "license": "0123456789",
        "password": "test",
        "complete_password": "test"
    }
    response = client.post("/register/", json=data)
    assert response.status_code == 400


def test_user_register_invalid_password():
    data = {
        "email": "test_email_2@mail.ru",
        "phone": "+78005553535",
        "first_name": "Имя",
        "last_name": "Отчество",
        "surname": "Фамилия",
        "license": "0123456789",
        "password": "test",
        "complete_password": "testttttt"
    }
    response = client.post("/register/", json=data)
    assert response.status_code == 401


def test_user_login_user_success():
    data = {
        "grant_type": "password",
        "username": "test_email@mail.ru",
        "password": "test"
    }
    response = client.post("/login/", data=data)
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"

    assert "access_token" in response.cookies
    access_token = response.cookies["access_token"]
    assert access_token == response_data["access_token"]


def test_user_login_user_invalid_credentials():
    data = {
        "grant_type": "password",
        "username": "test_incor@mail.ru",
        "password": "test_incor"
    }
    response = client.post("/login/", data=data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_user_update_user_data_success():
    data = {
        "grant_type": "password",
        "username": "test_email@mail.ru",
        "password": "test"
    }
    response = client.post("/login/", data=data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    data = {
        "email": "test_email_2@mail.ru",
        "password": "test_pass",
        "complete_password": "test_pass"
    }
    response = client.put("/update/", json=data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


def test_user_update_user_data_email_is_busy():
    data = {
        "grant_type": "password",
        "username": "test_email_2@mail.ru",
        "password": "test_pass"
    }
    response = client.post("/login/", data=data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    data = {
        "email": EMAIL_ADMIN,
        "password": "test_pass",
        "complete_password": "test_pass"
    }
    response = client.put("/update/", json=data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 400


def test_user_update_user_data_incorrect_password():
    data = {
        "grant_type": "password",
        "username": "test_email_2@mail.ru",
        "password": "test_pass"
    }
    response = client.post("/login/", data=data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    data = {
        "email": "test_email_2@mail.ru",
        "password": "test_pass",
        "complete_password": "test_pass_inc"
    }
    response = client.put("/update/", json=data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401


def test_user_reset_password_success():
    data = {
        "email": "test_email_2@mail.ru",
    }
    response = client.put("/reset_password/", json=data)
    assert response.status_code == 201


def test_user_reset_password_incorrect_email():
    data = {
        "email": "test_email_inc@mail.ru",
    }
    response = client.put("/reset_password/", json=data)
    assert response.status_code == 401


def test_user_create_new_password_incorrect_password():
    email = 'test_email_2@mail.ru'

    with Session(engine) as session:
        code = session.exec(select(User).where(User.email == email)).first().temp_data
    data = {
        "email": email,
        "code": code,
        "password": "test_pass_3",
        "complete_password": "test_pass_33333"
    }
    response = client.put('/create_new_password/', json=data)
    assert response.status_code == 401


def test_user_create_new_password_success():
    email = 'test_email_2@mail.ru'

    with Session(engine) as session:
        code = session.exec(select(User).where(User.email == email)).first().temp_data
    data = {
        "email": email,
        "code": code,
        "password": "test_pass_3",
        "complete_password": "test_pass_3"
    }
    response = client.put('/create_new_password/', json=data)
    assert response.status_code == 200


def test_user_create_new_password_incorrect_email_or_code():
    email = 'test_email_2@mail.ru'
    data = {
        "email": email,
        "code": '123456',
        "password": "test_pass_3",
        "complete_password": "test_pass_3"
    }
    response = client.put('/create_new_password/', json=data)
    assert response.status_code == 400


def test_user_me_success():
    data = {
        "grant_type": "password",
        "username": EMAIL_ADMIN,
        "password": PASS_ADMIN
    }
    response = client.post('/login/', data=data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    response = client.get('/me/', headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()['email'] == EMAIL_ADMIN


def test_user_me_not_authenticated():
    response = client.get('/me/')
    assert response.status_code == 401



# def test_car_and_rent_
#
#
# def test_payment_make_payment_success():




def test_dop_test_table():
    SQLModel.metadata.drop_all(engine)