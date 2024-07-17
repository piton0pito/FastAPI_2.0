from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr = Field(default='Email')  # почта
    phone: PhoneNumber = Field(default='+78005553535')
    first_name: str = Field(default='Имя')  # имя
    last_name: str = Field(default='Отчество')  # отчество
    surname: str = Field(default='Фамилия')  # фамилия
    license: str = Field(min_length=10, max_length=10)  # права
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class GetUser(BaseModel):
    email: EmailStr = Field(default='Email')  # почта
    first_name: str = Field(default='Имя')  # имя
    last_name: str = Field(default='Отчество')  # отчество
    surname: str = Field(default='Фамилия')  # фамилия
    license: str = Field(min_length=10, max_length=10)  # права




class UserUpdate(BaseModel):
    email: EmailStr = Field(default='Email')
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class CreateNewPassword(BaseModel):
    email: EmailStr = Field(default='Email')
    code: str = Field(default='Verify code')
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class AddCar(BaseModel):
    brand: str = Field(default='ваз')  # марка авто
    model: str = Field(default='ока')  # модель авто
    car_number: str = Field(default='ам777р777')  # гос_номер
    price_order: int = Field(default=50)  # цена аренды
    latitude: float  # широта
    longitude: float  # долгота


class GetCar(BaseModel):
    brand: str = Field(default='vas') # марка авто
    model: str = Field(default='1111') # модель авто
    # latitude: str = Field(default='0.0000000')  # широта
    # longitude: str = Field(default='0.0000000')  # долгота


class CarGeoDataUpdate(BaseModel):
    car_id: int
    latitude: float  # широта
    longitude: float  # долгота


class CarPriseUpdate(BaseModel):
    car_id: int
    price_order: int  # цена аренды


class PaymentCreate(BaseModel):
    card_number: str  # номер карты
    valid_thru_m: datetime = Field(default=datetime.now().month)  # дата валидности банковской карты
    valid_thru_y: datetime = Field(default=datetime.now().year)  # дата валидности банковской карты
    svv: str = Field(default='000')


class Email(BaseModel):
    email: str


class CarNumber(BaseModel):
    car_number: str
