from app.config import TEST_USER_EMAIL, TEST_USER_PASSWORD

from app.test.conftest import client
from app.test.data_for_test import login_user_data, reg_user_data, update_user_data, email_data, \
    create_new_password_data


def test_login_user(add_test_user_1, clear_database):
    response = client.post("/login/", data=login_user_data)
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"

    data = login_user_data
    data["password"] = TEST_USER_PASSWORD + 'incorrect'
    response = client.post("/login/", data=data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_register():
    data = reg_user_data
    data["complete_password"] = TEST_USER_PASSWORD + 'incorrect'
    response = client.post("/register/", json=data)
    assert response.status_code == 401
    data["complete_password"] = TEST_USER_PASSWORD

    response = client.post("/register/", json=reg_user_data)
    assert response.status_code == 201

    response = client.post("/register/", json=reg_user_data)
    assert response.status_code == 400


def test_update_user_data(add_test_user_1, add_test_user_2, clear_database):
    data = update_user_data
    response = client.put("/update/", json=update_user_data, headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 200

    data["email"] = TEST_USER_EMAIL + 'test'
    response = client.put("/update/", json=data, headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 400

    data["email"] = 'test' + TEST_USER_EMAIL
    data["complete_password"] = TEST_USER_PASSWORD
    response = client.put("/update/", json=data, headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 401


def test_reset_password(add_test_user_1, clear_database):
    data = email_data
    response = client.put("/reset_password/", json=email_data)
    assert response.status_code == 201

    data["email"] = TEST_USER_EMAIL + 'test'
    response = client.put("/reset_password/", json=email_data)
    assert response.status_code == 401
    data["email"] = TEST_USER_EMAIL


def test_create_new_password(add_test_user_1, get_code, clear_database):
    response = client.put('/create_new_password/', json=create_new_password_data)
    assert response.status_code == 400

    data = create_new_password_data
    data["code"] = get_code
    data["complete_password"] = TEST_USER_PASSWORD
    response = client.put('/create_new_password/', json=data)
    assert response.status_code == 401
    data["complete_password"] = TEST_USER_PASSWORD + 'test'

    data["code"] = get_code
    response = client.put('/create_new_password/', json=data)
    assert response.status_code == 200


def test_me_success(add_test_user_1):
    response = client.get('/me/', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 200
    assert response.json()['email'] == TEST_USER_EMAIL

    response = client.get('/me/')
    assert response.status_code == 401
