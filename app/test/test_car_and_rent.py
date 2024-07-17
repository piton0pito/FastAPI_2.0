from fastapi.security import HTTPBasic
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, select

from app.db import get_session
from app.main import app
from app.models import Car
from app.test.test_user import engine, override_get_session

client = TestClient(app)

app.dependency_overrides[get_session] = override_get_session

with Session(engine) as session:
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


def test_get_cars():
    data = {
        "brand": "",
        "model": ""
    }
    response = client.post('/get_cars/', json=data)
    assert response.status_code == 200
    assert response.json() == [{'model': 'x3', 'id': 1, 'brand': 'bmw', 'longitude': 0.0, 'car_number': 'в888вв88', 'status': 'active', 'latitude': 0.0, 'price_order': 50},
                               {'model': 'x5', 'id': 2, 'brand': 'bmw', 'longitude': 1.0, 'car_number': 'в111вв88', 'status': 'active', 'latitude': 1.0, 'price_order': 44},
                               {'model': 'gtr', 'id': 3, 'brand': 'nisan', 'longitude': 2.0, 'car_number': 'в004ко777', 'status': 'active', 'latitude': 2.0, 'price_order': 60}]


def test_get_car_brand():
    data = {
        "brand": "bmw",
        "model": ""
    }
    response = client.post('/get_cars/', json=data)
    assert response.status_code == 200
    assert response.json() == [
        {'longitude': 0.0, 'latitude': 0.0, 'price_order': 50, 'model': 'x3', 'brand': 'bmw', 'id': 1,
         'car_number': 'в888вв88', 'status': 'active'},
        {'longitude': 1.0, 'latitude': 1.0, 'price_order': 44, 'model': 'x5', 'brand': 'bmw', 'id': 2,
         'car_number': 'в111вв88', 'status': 'active'}]


def test_getr_car_brand_and_madel():
    data = {
        "brand": "bmw",
        "model": "x3"
    }
    response = client.post('/get_cars/', json=data)
    assert response.status_code == 200
    assert response.json() == [
        {'longitude': 0.0, 'latitude': 0.0, 'price_order': 50, 'model': 'x3', 'brand': 'bmw', 'id': 1,
         'car_number': 'в888вв88', 'status': 'active'}
    ]


def test_get_car_model():
    data = {
        "brand": "",
        "model": "x3"
    }
    response = client.post('/get_cars/', json=data)
    assert response.status_code == 200
    assert response.json() == {"msg": "First, choose a car brand"}

