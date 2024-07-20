from app.config import EMAIL_ADMIN, TEST_USER_EMAIL
from test.conftest import client
from test.data_for_test import add_car_data


def test_create_first_admin(clear_database):
    response = client.post('/admin/create_first_admin/')
    assert response.status_code == 201
    response = client.post('/admin/create_first_admin/')
    assert response.status_code == 400


def test_get_all_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["email"] == EMAIL_ADMIN

    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_get_verify_user(add_test_admin_1, add_test_user_2, clear_database):
    response = client.get('/admin/get_verify_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[0]["id"] == 2
    assert response.json()[0]["email"] == TEST_USER_EMAIL + 'test'

    response = client.get('/admin/get_verify_user/', headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 403


def test_get_verify_user_xlsx(add_test_admin_1, add_test_user_2, clear_database):
    response = client.get('/admin/get_verify_user/xlsx', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "multipart/form-data"
    assert response.headers["content-disposition"] == 'attachment; filename="verify_users.xlsx"'

    response = client.get('/admin/get_verify_user/xlsx', headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 403


def test_get_no_verify_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.get('/admin/get_no_verify_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[0]["id"] == 2
    assert response.json()[0]["email"] == TEST_USER_EMAIL

    response = client.get('/admin/get_no_verify_user/', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_get_no_verify_user_xlsx(add_test_admin_1, add_test_user_2, clear_database):
    response = client.get('/admin/get_no_verify_user/xlsx', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "multipart/form-data"
    assert response.headers["content-disposition"] == 'attachment; filename="no_verify_users.xlsx"'

    response = client.get('/admin/get_no_verify_user/xlsx', headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 403


def test_verify_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.put('/admin/verify_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_verify_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[0]["id"] == 2

    response = client.put('/admin/verify_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The user has already been verified'

    response = client.put('/admin/verify_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/verify_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_BAN_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["role"] == "BAN"

    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The user has already been blocked'

    response = client.put('/admin/BAN_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_un_BAN_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.put('/admin/un_BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["role"] == "no_verify"

    response = client.put('/admin/un_BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The user is not blocked'

    response = client.put('/admin/un_BAN_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/un_BAN_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_make_super_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.put('/admin/make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["role"] == "super_user"

    response = client.put('/admin/make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "The user is already a super user"

    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.put('/admin/make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "The user has already been blocked"

    response = client.put('/admin/make_super_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/make_super_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_un_make_super_user(add_test_admin_1, add_test_admin_2, add_test_user_1, clear_database):
    response = client.put('/admin/un_make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["role"] == "no_verify"

    response = client.put('/admin/un_make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "The user is not a super user"

    response = client.put('/admin/un_make_super_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/un_make_super_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_get_all_car(add_test_admin_1, add_cars, clear_database):
    response = client.get('/admin/get_all_cars', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json() == [
        {'model': 'x3', 'id': 1, 'brand': 'bmw', 'longitude': 0.0, 'car_number': 'в888вв88', 'status': 'active',
         'latitude': 0.0, 'price_order': 50},
        {'model': 'x5', 'id': 2, 'brand': 'bmw', 'longitude': 1.0, 'car_number': 'в111вв88', 'status': 'active',
         'latitude': 1.0, 'price_order': 44},
        {'model': 'gtr', 'id': 3, 'brand': 'nisan', 'longitude': 2.0, 'car_number': 'в004ко777', 'status': 'active',
         'latitude': 2.0, 'price_order': 60}]


def test_add_car(add_test_admin_1, add_test_user_1, clear_database):
    response = client.post('/admin/add_car/', json=add_car_data,
                           headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('admin/get_all_cars/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[0]["car_number"] == add_car_data["car_number"]

    response = client.post('/admin/add_car/', json=add_car_data,
                           headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The car with this number is already registered'

    response = client.post('/admin/add_car/', json=add_car_data,
                           headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_del_car(add_test_admin_1, add_test_user_1, add_cars, clear_database):
    response = client.delete('/admin/del_car/1',
                             headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('admin/get_all_cars/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json() == [
        {'model': 'x5', 'id': 2, 'brand': 'bmw', 'longitude': 1.0, 'car_number': 'в111вв88', 'status': 'active',
         'latitude': 1.0, 'price_order': 44},
        {'model': 'gtr', 'id': 3, 'brand': 'nisan', 'longitude': 2.0, 'car_number': 'в004ко777', 'status': 'active',
         'latitude': 2.0, 'price_order': 60}
    ]

    response = client.delete('/admin/del_car/9999',
                             headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'Car not found'

    response = client.delete('/admin/del_car/1',
                             headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_service_car(add_test_admin_1, add_test_user_1, add_cars, clear_database):
    response = client.put('/admin/service_car/1',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('admin/get_all_cars/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json() == [
        {'model': 'x3', 'id': 1, 'brand': 'bmw', 'longitude': 0.0, 'car_number': 'в888вв88', 'status': 'service',
         'latitude': 0.0, 'price_order': 50},
        {'model': 'x5', 'id': 2, 'brand': 'bmw', 'longitude': 1.0, 'car_number': 'в111вв88', 'status': 'active',
         'latitude': 1.0, 'price_order': 44},
        {'model': 'gtr', 'id': 3, 'brand': 'nisan', 'longitude': 2.0, 'car_number': 'в004ко777', 'status': 'active',
         'latitude': 2.0, 'price_order': 60}]

    response = client.put('/admin/service_car/1',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The car is already in service'

    response = client.put('/admin/service_car/9999',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'Car not found'

    response = client.put('/admin/service_car/1',
                          headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_active_car(add_test_admin_1, add_test_user_1, add_cars, clear_database):
    response = client.put('/admin/service_car/1',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.put('/admin/active_car/1',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('admin/get_all_cars/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json() == [
        {'model': 'x3', 'id': 1, 'brand': 'bmw', 'longitude': 0.0, 'car_number': 'в888вв88', 'status': 'active',
         'latitude': 0.0, 'price_order': 50},
        {'model': 'x5', 'id': 2, 'brand': 'bmw', 'longitude': 1.0, 'car_number': 'в111вв88', 'status': 'active',
         'latitude': 1.0, 'price_order': 44},
        {'model': 'gtr', 'id': 3, 'brand': 'nisan', 'longitude': 2.0, 'car_number': 'в004ко777', 'status': 'active',
         'latitude': 2.0, 'price_order': 60}]

    response = client.put('/admin/active_car/1',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The car is already in active'

    response = client.put('/admin/active_car/9999',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'Car not found'

    response = client.put('/admin/active_car/1',
                          headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_no_active_car(add_test_admin_1, add_test_user_1, add_cars, clear_database):
    response = client.put('/admin/no_active_car/1',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('admin/get_all_cars/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json() == [
        {'model': 'x3', 'id': 1, 'brand': 'bmw', 'longitude': 0.0, 'car_number': 'в888вв88', 'status': 'no_active',
         'latitude': 0.0, 'price_order': 50},
        {'model': 'x5', 'id': 2, 'brand': 'bmw', 'longitude': 1.0, 'car_number': 'в111вв88', 'status': 'active',
         'latitude': 1.0, 'price_order': 44},
        {'model': 'gtr', 'id': 3, 'brand': 'nisan', 'longitude': 2.0, 'car_number': 'в004ко777', 'status': 'active',
         'latitude': 2.0, 'price_order': 60}]

    response = client.put('/admin/no_active_car/1',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The car is already no_active'

    response = client.put('/admin/no_active_car/9999',
                          headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'Car not found'

    response = client.put('/admin/no_active_car/1',
                          headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403
