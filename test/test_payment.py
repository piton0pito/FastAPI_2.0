from test.conftest import client
from test.data_for_test import end_rent_data


def test_make_payment(add_test_user_2, add_cars, clear_database):
    response = client.post('/rent_car/', json={"car_number": 'в888вв88'},
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    response = client.put('/end_rent_car/', json=end_rent_data, headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    response = client.post('/make_payment/', json=end_rent_data,
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200

    response = client.post('/make_payment/', json=end_rent_data,
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    assert response.json() == "You don't have any unpaid trips"


def test_my_payment(add_test_user_2, add_cars, clear_database):
    response = client.get('/my_payment/',
                          headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    assert response.json() == "You don't have any payments"

    response = client.post('/rent_car/', json={"car_number": 'в888вв88'},
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    response = client.put('/end_rent_car/', json=end_rent_data, headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200

    response = client.get('/my_payment/',
                          headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["user_id"] == 1
    assert response.json()[0]["status"] == 'waiting'

    response = client.post('/make_payment/', json=end_rent_data,
                           headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200

    response = client.get('/my_payment/',
                          headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200
    assert response.json()[0]["status"] == 'payment'

    response = client.get('/my_payment/')
    assert response.status_code == 401