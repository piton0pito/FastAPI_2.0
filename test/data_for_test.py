from app.config import TEST_USER_EMAIL, TEST_USER_PHONE, TEST_USER_FIRST_NAME, TEST_USER_LAST_NAME, TEST_USER_SURNAME, \
    TEST_USER_LICENSE, TEST_USER_PASSWORD, EMAIL_ADMIN, PASS_ADMIN
from app.models import User, Car
from app.utils import hash_password

reg_user_data = {
    "email": TEST_USER_EMAIL,
    "phone": TEST_USER_PHONE,
    "first_name": TEST_USER_FIRST_NAME,
    "last_name": TEST_USER_LAST_NAME,
    "surname": TEST_USER_SURNAME,
    "license": TEST_USER_LICENSE,
    "password": TEST_USER_PASSWORD,
    "complete_password": TEST_USER_PASSWORD
}

login_user_data = {
    "grant_type": "password",
    "username": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD
}

login_admin_data = {
    "grant_type": "password",
    "username": EMAIL_ADMIN,
    "password": PASS_ADMIN
}

update_user_data = {
    "email": TEST_USER_EMAIL + 'test',
    "password": TEST_USER_PASSWORD + 'test',
    "complete_password": TEST_USER_PASSWORD + 'test'
}

create_new_password_data = {
    "email": TEST_USER_EMAIL,
    "code": "000000",
    "password": TEST_USER_PASSWORD + 'test',
    "complete_password": TEST_USER_PASSWORD + 'test'
}

email_data = {"email": TEST_USER_EMAIL}

end_rent_data = {
    "card_number": "string",
    "valid_thru_m": "7",
    "valid_thru_y": "2024",
    "svv": "000"
}

add_car_data = {
    "brand": "ваз",
    "model": "ока",
    "car_number": "ам777р777",
    "price_order": 50,
    "latitude": 0,
    "longitude": 0
}

# hash_pass = hash_password(TEST_USER_PASSWORD)
# user_1 = User(email=TEST_USER_EMAIL,
#               hash_password=hash_pass,
#               first_name=TEST_USER_FIRST_NAME,
#               last_name=TEST_USER_LAST_NAME,
#               surname=TEST_USER_SURNAME,
#               license=TEST_USER_LICENSE)
#
# user_2 = User(email=TEST_USER_EMAIL + 'test',
#               hash_password=hash_pass,
#               first_name=TEST_USER_FIRST_NAME,
#               last_name=TEST_USER_LAST_NAME,
#               surname=TEST_USER_SURNAME,
#               license=TEST_USER_LICENSE,
#               )
# user_2.verify_user()
#
# hash_pass = hash_password(PASS_ADMIN)
# admin_1 = User(email=EMAIL_ADMIN,
#                hash_password=hash_pass,
#                first_name='admin',
#                last_name='admin',
#                surname='admin',
#                license='0000000000')
# admin_1.super_user()
#
# admin_2 = User(email=EMAIL_ADMIN + 'test',
#                hash_password=hash_pass,
#                first_name='admin',
#                last_name='admin',
#                surname='admin',
#                license='0000000000')
# admin_2.super_user()
#
# car1 = Car(
#     brand='bmw',
#     model='x3',
#     latitude=0.0000000,
#     longitude=0.0000000,
#     car_number='в888вв88',
#     price_order=50
# )
# car2 = Car(
#     brand='bmw',
#     model='x5',
#     latitude=1.0000000,
#     longitude=1.0000000,
#     car_number='в111вв88',
#     price_order=44
# )
# car3 = Car(
#     brand='nisan',
#     model='gtr',
#     latitude=2.0000000,
#     longitude=2.0000000,
#     car_number='в004ко777',
#     price_order=60
# )
