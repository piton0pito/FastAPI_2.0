from pydantic import BaseModel, Field
from datetime import datetime


class UserCreate(BaseModel):
    email: str  # почта
    first_name: str  # имя
    last_name: str  # отчество
    surname: str  # фамилия
    license: str = Field(min_length=10, max_length=10)  # права
    password: str
    complete_password: str



class UserUpdate(BaseModel):
    email: str
    password: str
    complete_password: str


class CreateNewPassword(BaseModel):
    email: str
    code: str
    password: str
    complete_password: str


class AddCar(BaseModel):
    brand: str  # марка авто
    model: str  # модель авто
    car_number: str  # гос_номер
    price_order: int  # цена аренды
    latitude: float  # широта
    longitude: float  # долгота


class GetCar(BaseModel):
    brand: str = Field(default=None) # марка авто
    model: str = Field(default=None) # модель авто
    latitude: float  # широта
    longitude: float  # долгота


class CarGeoDataUpdate(BaseModel):
    car_id: int
    latitude: float  # широта
    longitude: float  # долгота


class CarPriseUpdate(BaseModel):
    car_id: int
    price_order: int  # цена аренды


class PaymentCreate(BaseModel):
    card_number: str  # номер карты
    valid_thru: datetime    # дата валидности банковской карты
    svv: str
