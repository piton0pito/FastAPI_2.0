from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.models import User, Car
from app.db import get_session
from app.schemas import AddCar
from app.utils import verify_access_token, get_xlsx

router = APIRouter(prefix='/admin', tags=['admin'],
                   responses={404: {"description": "Not found"}})

@router.get('/get_all_user/')
def get_all_user(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role != 'super_user':
        raise HTTPException(status_code=403)
    users = session.exec(select(User)).all()
    return users


@router.get('/get_verify_user/')
def get_verify_user(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role != 'super_user':
        raise HTTPException(status_code=403)
    users = session.exec(select(User).where(User.role == 'verify')).all()
    return users


@router.get('/get_verify_user/xlsx')
def get_verify_user(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role != 'super_user':
        raise HTTPException(status_code=403)
    name = 'verify_users'
    users = session.exec(select(User).where(User.role == 'verify')).all()
    get_xlsx(users, f'{name}.xlsx')
    return FileResponse(path=f'{name}.xlsx', filename=f'{name}.xlsx', media_type='multipart/form-data')


@router.get('/get_no_verify_user/')
def get_no_verify_user(su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    users = session.exec(select(User).where(User.role == 'no_verify')).all()
    return users


@router.get('/get_no_verify_user/xlsx')
def get_no_verify_user_xlsx(su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    name = 'no_verify_users'
    users = session.exec(select(User).where(User.role == 'no_verify')).all()
    get_xlsx(users, f'{name}.xlsx')
    return FileResponse(path=f'{name}.xlsx', filename=f'{name}.xlsx', media_type='multipart/form-data')


@router.get('/verify_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role == 'verify':
        raise HTTPException(status_code=400, detail='The user has already been verified')
    user.verify_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/BAN_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role == 'BAN':
        raise HTTPException(status_code=400, detail='The user has already been blocked')
    user.ban_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/un_BAN_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role != 'BAN':
        raise HTTPException(status_code=400, detail='The user is not blocked')
    user.un_ban_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.delete('/del_user/{user_id}')
def del_user(user_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    session.delete(user)
    session.commit()
    raise HTTPException(status_code=200)


@router.put('/make_super_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role == 'BAN':
        raise HTTPException(status_code=400, detail='The user has already been blocked')
    if user.role == 'super_user':
        raise HTTPException(status_code=400, detail='The user is already a super user')
    user.super_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/un_make_super_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role != 'super_user':
        raise HTTPException(status_code=400, detail='The user is not a super user')
    user.un_super_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)



@router.post('/add_car/')
def add_car(data: AddCar, session: Session = Depends(get_session), su_user: User = Depends(verify_access_token)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    car = Car(brand=data.brand,
              model=data.model,
              latitude=data.latitude,
              longitude=data.longitude,
              car_number=data.car_number,
              price_order=data.price_order
              )
    session.add(car)
    session.commit()
    raise HTTPException(status_code=200)


@router.delete('/del_car/{car_id}')
def add_car(car_id, session: Session = Depends(get_session), su_user: User = Depends(verify_access_token)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    car = session.exec(select(Car).where(Car.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail='Car not found')
    session.delete(car)
    session.commit()
    raise HTTPException(status_code=200)


@router.put('/service_car/{car_id}')
def add_car(car_id, session: Session = Depends(get_session), su_user: User = Depends(verify_access_token)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    car = session.exec(select(Car).where(Car.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail='Car not found')
    if car.status == 'service':
        raise HTTPException(status_code=400, detail='The car is already in service')
    car.service()
    session.add(car)
    session.commit()
    session.refresh(car)
    raise HTTPException(status_code=200)


@router.put('/active_car/{car_id}')
def add_car(car_id, session: Session = Depends(get_session), su_user: User = Depends(verify_access_token)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    car = session.exec(select(Car).where(Car.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail='Car not found')
    if car.status == 'active':
        raise HTTPException(status_code=400, detail='The car is already in active')
    car.active()
    session.add(car)
    session.commit()
    session.refresh(car)
    raise HTTPException(status_code=200)


@router.put('/no_active_car/{car_id}')
def add_car(car_id, session: Session = Depends(get_session), su_user: User = Depends(verify_access_token)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    car = session.exec(select(Car).where(Car.id == car_id)).first()
    if not car:
        raise HTTPException(status_code=404, detail='Car not found')
    if car.status == 'no_active':
        raise HTTPException(status_code=400, detail='The car is already no_active')
    car.no_active()
    session.add(car)
    session.commit()
    session.refresh(car)
    raise HTTPException(status_code=200)
