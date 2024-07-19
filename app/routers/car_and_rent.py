from fastapi import APIRouter, HTTPException, Response, Depends
from sqlmodel import Session, select
from datetime import datetime

from app.db import get_session
from app.models import Car, User, Rent, Payment
from app.schemas import GetCar, CarGeoDataUpdate, AddCar, PaymentCreate, CarNumber
from app.utils import verify_access_token, get_delta_time, get_car

router = APIRouter(tags=['car_and_rent'],
                   responses={404: {"description": "Not found"}})


@router.post('/get_cars/')      #это post запрос, так как для get запроса слишком большой обьем отправляемой инормации
def get_car_temp(data: GetCar, session: Session = Depends(get_session)):
    if not data.brand and not data.model:
        cars = session.exec(select(Car).where(Car.status == 'active')).all()
    elif data.brand and not data.model:
        cars = session.exec(select(Car).where(Car.brand == data.brand).where(Car.status == 'active')).all()
    elif data.brand and data.model:
        cars = session.exec(select(Car).where(Car.brand == data.brand).where(Car.model == data.model).where(Car.status == 'active')).all()
    else:
        return {'msg': 'First, choose a car brand'}
    return cars



@router.post('/rent_car/')
def rent_car(car_number: CarNumber, session: Session = Depends(get_session), user: User = Depends(verify_access_token)):
    if user.role == 'no_verify':
        raise HTTPException(status_code=403, detail='You have not passed verification')
    if user.role == 'BAN':
        raise HTTPException(status_code=403, detail='You are BANed!!!')
    car = session.exec(select(Car).where(Car.car_number == car_number.car_number)).first()
    if session.exec(select(Payment).where(Payment.user_id == user.id).where(Payment.status == 'waiting')).first():
        raise HTTPException(status_code=402,
                            detail="You have an unpaid trip. Pay for the trip for further use of the service")
    if not car:
        raise HTTPException(status_code=400, detail='Incorrect car number')
    if session.exec(select(Rent).where(Rent.user_id == user.id).where(Rent.data_rent_end == None)).first():
        raise HTTPException(status_code=429, detail="You didn't complete the last trip. To continue, complete the trip")

    car.no_active()
    rent = Rent(user_id=user.id, car_id=car.id)
    session.add(car)
    session.add(rent)
    session.commit()
    session.refresh(car)
    raise HTTPException(status_code=200)


@router.put('/end_rent_car/')
def end_rent_car(data: PaymentCreate, user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    rent = session.exec(select(Rent).where(Rent.user_id == user.id).where(Rent.data_rent_end == None)).first()
    if not rent:
        raise HTTPException(status_code=400, detail="You don't have any trips started")
    if user.role == 'BAN':
        raise HTTPException(status_code=403, detail='You are BANed!!!')
    car = session.exec(select(Car).where(Car.id == rent.car_id)).first()
    rent.end()
    car.active()
    payment = Payment(rent_id=rent.id, user_id=user.id,
                      prise=(car.price_order * get_delta_time(rent.data_rent_start, rent.data_rent_end)),
                      card_number=data.card_number)
    session.add(rent)
    session.add(car)
    session.add(payment)
    session.commit()
    session.refresh(rent)
    session.refresh(car)
    # здесь должна быть функция для обновления геолокации машины
    raise HTTPException(status_code=200)


@router.get('/my_rent/')
def get_my_rent(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    my_rents = session.exec(select(Rent).where(Rent.user_id == user.id)).all()
    if not my_rents:
        return "You don't have any trips"
    return my_rents
