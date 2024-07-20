import pytest
from fastapi.security import HTTPBasic
from sqlalchemy import create_engine, delete
from sqlmodel import Session, SQLModel, select
from starlette.testclient import TestClient

from app.config import TEST_USER_EMAIL, TEST_USER_FIRST_NAME, TEST_USER_LAST_NAME, TEST_USER_PASSWORD, \
    TEST_USER_LICENSE, TEST_USER_SURNAME, EMAIL_ADMIN, PASS_ADMIN
from app.db import get_session
from app.main import app
from app.models import User, Car, Payment, Rent
# from app.test.data_for_test import user_1, user_2, admin_1, admin_2, car1, car2, car3
from test.data_for_test import email_data
from app.utils import hash_password

engine = create_engine("sqlite:///./test_data_base.db")
security = HTTPBasic()
client = TestClient(app)


def override_get_session():
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True, scope='session')
def over_depends():
    app.dependency_overrides[get_session] = override_get_session
    yield


@pytest.fixture(scope='function')
def session():
    yield Session(engine)


@pytest.fixture(autouse=True, scope='session')
def setup():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope='function', autouse=False)
def clear_database(session):
    yield
    session = Session(engine)
    session.exec(delete(User))
    session.exec(delete(Car))
    session.exec(delete(Payment))
    session.exec(delete(Rent))
    session.commit()
    session.close()


@pytest.fixture(scope="function")
def add_test_user_1(session):
    hash_pass = hash_password(TEST_USER_PASSWORD)
    user_1 = User(email=TEST_USER_EMAIL,
                  hash_password=hash_pass,
                  first_name=TEST_USER_FIRST_NAME,
                  last_name=TEST_USER_LAST_NAME,
                  surname=TEST_USER_SURNAME,
                  license=TEST_USER_LICENSE)
    session.add(user_1)
    session.commit()
    session.close()
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def add_test_user_2(session):
    hash_pass = hash_password(TEST_USER_PASSWORD)
    user_2 = User(email=TEST_USER_EMAIL + 'test',
                  hash_password=hash_pass,
                  first_name=TEST_USER_FIRST_NAME,
                  last_name=TEST_USER_LAST_NAME,
                  surname=TEST_USER_SURNAME,
                  license=TEST_USER_LICENSE,
                  )
    user_2.verify_user()
    session.add(user_2)
    session.commit()
    session.close()
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": TEST_USER_EMAIL + 'test',
        "password": TEST_USER_PASSWORD
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def add_test_admin_1(session):
    hash_pass = hash_password(PASS_ADMIN)
    admin_1 = User(email=EMAIL_ADMIN,
                   hash_password=hash_pass,
                   first_name='admin',
                   last_name='admin',
                   surname='admin',
                   license='0000000000')
    admin_1.super_user()
    session.add(admin_1)
    session.commit()
    session.close()
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": EMAIL_ADMIN,
        "password": PASS_ADMIN
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def add_test_admin_2(session):
    hash_pass = hash_password(PASS_ADMIN)
    admin_2 = User(email=EMAIL_ADMIN + 'test',
                   hash_password=hash_pass,
                   first_name='admin',
                   last_name='admin',
                   surname='admin',
                   license='0000000000')
    admin_2.super_user()
    session.add(admin_2)
    session.commit()
    session.close()
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": EMAIL_ADMIN + 'test',
        "password": PASS_ADMIN
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope='function')
def get_code(session):
    response = client.put("/reset_password/", json=email_data)
    assert response.status_code == 201
    code = session.exec(select(User)).first().temp_data
    session.close()
    return code


@pytest.fixture(scope='function')
def add_cars():
    session = Session(engine)
    car1 = Car(
        brand='bmw',
        model='x3',
        latitude=0.0000000,
        longitude=0.0000000,
        car_number='в888вв88',
        price_order=50
    )
    car2 = Car(
        brand='bmw',
        model='x5',
        latitude=1.0000000,
        longitude=1.0000000,
        car_number='в111вв88',
        price_order=44
    )
    car3 = Car(
        brand='nisan',
        model='gtr',
        latitude=2.0000000,
        longitude=2.0000000,
        car_number='в004ко777',
        price_order=60
    )
    session.add(car1)
    session.add(car2)
    session.add(car3)
    session.commit()
    session.close()
    yield
