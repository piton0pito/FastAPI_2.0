from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional
from datetime import datetime
from hashlib import sha256


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    hash_password: str  # хэш пароля
    role: str = Field(default='no_verify')  # роль пользователя super_user, verify, no_verify, BAN
    email: str  # почта
    first_name: str  # имя
    last_name: str  # отчество
    surname: str  # фамилия
    license: str = Field(min_length=10, max_length=10)  # права
    date_reg: datetime = Field(default_factory=datetime.utcnow)  # дата регистрации
    temp_data: str = Field(nullable=True)

    def verify_password(self, password):
        return self.hash_password == sha256(password.encode()).hexdigest()

    def verify_user(self):
        self.role = 'verify'

    def ban_user(self):
        self.role = 'BAN'

    def un_ban_user(self):
        self.role = 'no_verify'

    def super_user(self):
        self.role = 'super_user'

    def un_super_user(self):
        self.role = 'no_verify'


class Car(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    brand: str  # марка авто
    model: str  # модель авто
    latitude: float  # широта
    longitude: float  # долгота
    car_number: str  # гос_номер
    price_order: int  # цена аренды
    status: str = Field(default='active')

    def service(self):
        self.status = 'service'

    def active(self):
        self.status = 'active'

    def no_active(self):
        self.status = 'no active'


class Rent(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key='user.id')  # id_пользователя
    car_id: int = Field(foreign_key='car.id')  # id_машины
    data_rent_start: datetime = Field(default_factory=datetime.utcnow)  # дата аренды начало
    data_rent_end: datetime = None  # дата аренды конец
    status: str = Field(default='continues')  # 'continues' или 'end'

    def end(self):
        self.status = 'end'


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    rent_id: int = Field(default=None, foreign_key='rent.id')  # id_аренды
    user_id: int = Field(default=None, foreign_key='user.id')  # id_пользователя
    prise: int
    card_number: str  # номер карты
    # valid_thru: datetime  # дата валидности банковской карты
    # svv: str = Field(min_length=3, max_length=3)
    data: datetime = Field(default_factory=datetime.utcnow)  # дата оплаты
    status: str = Field(default='waiting')  # waiting or payment

    def payment(self):
        self.status = 'payment'
