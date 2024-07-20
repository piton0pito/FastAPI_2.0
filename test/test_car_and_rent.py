from test.conftest import client
from test.data_for_test import end_rent_data


def test_get_cars(add_cars, clear_database):
    data = {
        "brand": "",
        "model": ""
    }
    response = client.post('/get_cars/', json=data)
    assert response.status_code == 200
    assert response.json() == [
        {'model': 'x3', 'id': 1, 'brand': 'bmw', 'longitude': 0.0, 'car_number': 'в888вв88', 'status': 'active',
         'latitude': 0.0, 'price_order': 50},
        {'model': 'x5', 'id': 2, 'brand': 'bmw', 'longitude': 1.0, 'car_number': 'в111вв88', 'status': 'active',
         'latitude': 1.0, 'price_order': 44},
        {'model': 'gtr', 'id': 3, 'brand': 'nisan', 'longitude': 2.0, 'car_number': 'в004ко777', 'status': 'active',
         'latitude': 2.0, 'price_order': 60}]


def test_get_car_brand(add_cars, clear_database):
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


def test_getr_car_brand_and_madel(add_cars, clear_database):
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


def test_get_car_model(add_cars, clear_database):
    data = {
        "brand": "",
        "model": "x3"
    }
    response = client.post('/get_cars/', json=data)
    assert response.status_code == 200
    assert response.json() == {"msg": "First, choose a car brand"}


def test_rent_car(add_test_user_1, add_test_user_2, add_cars, clear_database):
    response = client.post('/rent_car/', json={"car_number": 'в888вв88'},
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200

    response = client.post('/rent_car/', json={"car_number": 'в888вв88'},
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 429
    assert response.json()["detail"] == "You didn't complete the last trip. To continue, complete the trip"

    response = client.post('/rent_car/', json={"car_number": 'о000оо00'},
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'Incorrect car number'

    response = client.post('/rent_car/', json={"car_number": 'в888вв88'},
                           headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403
    assert response.json()["detail"] == 'You have not passed verification'

    response = client.put('/end_rent_car/', json=end_rent_data, headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    response = client.post('/rent_car/', json={"car_number": 'в888вв88'},
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 402
    assert response.json()["detail"] == "You have an unpaid trip. Pay for the trip for further use of the service"


def test_end_rent_car(add_test_user_2, add_cars, clear_database):
    response = client.post('/rent_car/', json={"car_number": 'в888вв88'},
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    response = client.put('/end_rent_car/', json=end_rent_data, headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200

    response = client.put('/end_rent_car/', json=end_rent_data, headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "You don't have any trips started"


def test_my_rent(add_test_user_2, add_cars, clear_database):
    response = client.post('/rent_car/', json={"car_number": 'в888вв88'},
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200

    response = client.get('/my_rent/', headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    assert response.json()[0]["car_id"] == 1
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["data_rent_end"] is None
    assert response.json()[0]["status"] == 'continues'

    response = client.get('/my_rent/')
    assert response.status_code == 401
