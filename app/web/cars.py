from fastapi import APIRouter, Request, Depends, responses, status
from fastapi.templating import Jinja2Templates
from app.models import Car, User, Payment, Rent
from sqlmodel import Session, select
from app.db import get_session
from jwt import decode
from app.config import SECRET_KEY, ALGORITHM
from app.utils import get_delta_time

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/")
def home(request: Request, db: Session=Depends(get_session)):
    cars = db.query(Car).all()
    return templates.TemplateResponse("homepage.html", {"request": request, "cars": cars})


@router.get("/detail/{id}")
def car_detail(request: Request, id: int, db: Session=Depends(get_session)):
    car = db.query(Car).filter(Car.id == id).first()
    return templates.TemplateResponse("car_detail.html", {"request": request, "car": car})


@router.get("/payments")
def payments(request: Request):
    return templates.TemplateResponse("payments.html", {"request": request})


@router.post("/payments")
async def payments(request: "Request", db:Session=Depends(get_session)):
    form = await request.form()
    card_number = form.get("card_number")
    valid_thru_m = form.get("valid_thru_m")
    valid_thru_y = form.get("valid_thru_y")
    svv = form.get("svv")
    errors = []
    if not card_number:
        errors.append("Не заполнели")
        return templates.TemplateResponse("payments.html", {"request": request})
    if not svv:
        errors.append("Не заполнели")
        return templates.TemplateResponse("payments.html", {"request": request})
    token = request.cookies.get("access_token")
    if token is None:
        errors.append("Не вошли")
        return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            errors.append("Cначала создайте учетную запись или войдите в систему")
            return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
        else:
            payment = db.exec(select(Payment).where(Payment.user_id == user.id).where(Payment.status == 'waiting')).first()
            if not payment:
                errors.append("У вас нет неоплаченных поездок")
                return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
            payment.payment()
            db.add(payment)
            db.commit()
            db.refresh(payment)
            msg = "Оплата прошла успешно!"
            return templates.TemplateResponse("payments.html", {"request": request, "msg": msg})




@router.get("/start_rent")
def start_rent(request: Request):
    return templates.TemplateResponse("start_rent.html", {"request": request})


@router.post("/start_rent")
async def start_rent(request: "Request", db:Session=Depends(get_session)):
    form = await request.form()
    car_number = form.get("car_number")
    errors = []
    if not car_number:
        errors.append("Введите номер машины")
        return templates.TemplateResponse("start_rent.html", {"request": request, "errors": errors})
    token = request.cookies.get("access_token")
    if not token:
        errors.append("Не авторизовались")
        return templates.TemplateResponse("start_rent.html", {"request": request, "errors": errors})
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            errors.append("Cначала создайте учетную запись или войдите в систему")
            return templates.TemplateResponse("start_rent.html", {"request": request, "errors": errors})
        if user.role == 'no_verify':
            errors.append("Вы не прошли проверку")
            return templates.TemplateResponse("start_rent.html", {"request": request, "errors": errors})
        car = db.exec(select(Car).where(Car.car_number == car_number)).first()
        if db.exec(select(Payment).where(Payment.user_id == user.id).where(Payment.status == 'waiting')).first():
            errors.append("У вас неоплаченная поездка")
            return templates.TemplateResponse("start_rent.html", {"request": request, "errors": errors})
        if not car:
            errors.append("Неправильный номер машины")
            return templates.TemplateResponse("start_rent.html", {"request": request, "errors": errors})
        if db.exec(select(Rent).where(Rent.user_id == user.id).where(Rent.data_rent_end == None)).first():
            errors.append("Вы не завершили последнюю поездку. Чтобы продолжить, завершите.")
            return templates.TemplateResponse("start_rent.html", {"request": request, "errors": errors})
        car.no_active()
        rent = Rent(user_id=user.id, car_id=car.id)
        db.add(car)
        db.add(rent)
        db.commit()
        db.refresh(car)
        return responses.RedirectResponse("/end_rent", status_code=status.HTTP_302_FOUND)


@router.get("/end_rent")
def end_rent(request: Request):
    return templates.TemplateResponse("end_rent.html", {"request": request})


@router.post("/end_rent")
async def end_rent(request: "Request", db:Session=Depends(get_session)):
    form = await request.form()
    car_number = form.get("car_number")
    card_number = form.get("card_number")
    errors = []
    if not car_number:
        errors.append("Введите номер машины")
        return templates.TemplateResponse("end_rent.html", {"request": request, "errors": errors})
    token = request.cookies.get("access_token")
    if token is None:
        errors.append("Не авторизовались")
        return templates.TemplateResponse("end_rent.html", {"request": request, "errors": errors})
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            errors.append("Cначала создайте учетную запись или войдите в систему")
            return templates.TemplateResponse("end_rent.html", {"request": request, "errors": errors})
        rent = db.exec(select(Rent).where(Rent.user_id == user.id).where(Rent.data_rent_end == None)).first()
        if not rent:
            errors.append("У вас нет начатых поездок")
            return templates.TemplateResponse("end_rent.html", {"request": request, "errors": errors})
        car = db.exec(select(Car).where(Car.id == rent.car_id)).first()
        rent_id = rent.id
        rent.end()
        car.active()
        print(rent.id)
        payment = Payment(rent_id=rent_id, user_id=user.id, prise=(car.price_order * get_delta_time(rent.data_rent_start, rent.data_rent_end)),
                      card_number=card_number, data=rent.data_rent_end, status="waiting")
        db.add(rent)
        db.add(car)
        db.add(payment)
        db.commit()
        db.refresh(rent)
        db.refresh(car)
        return responses.RedirectResponse("/payments", status_code=status.HTTP_302_FOUND)


@router.get("/add_car")
def create_car(request: Request):
    return templates.TemplateResponse("add_car.html", {"request": request})


@router.post("/add_car")
async def create_car(request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    brand = form.get("brand")
    model = form.get("model")
    car_number = form.get("car_number")
    price_order = form.get("price_order")
    latitude = form.get("latitude")
    longitude = form.get("longitude")

    errors = []

    if len(car_number) != 9:
        errors.append("Номер должен состоять из 9 символов!")
        return templates.TemplateResponse("add_car.html", {"request": request, "errors": errors})
    if latitude is None:
        errors.append("Введите широту")
        return templates.TemplateResponse("add_car.html", {"request": request, "errors": errors})

    car = Car(brand=brand,
              model=model,
              car_number=car_number,
              price_order=price_order,
              latitude=latitude,
              longitude=longitude,
              )


    db.add(car)
    db.commit()
    db.refresh(car)
    msg = "Машина добавлена!"
    return templates.TemplateResponse("add_car.html", {"request": request, "msg": msg})


@router.get("/del_car")
def del_car(request: Request, db:Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    if token is None:
        errors.append("Вы не авторизовались/зарегистрировались")
        return templates.TemplateResponse("del_car.html", {"request": request, "errors": errors})
    cars = db.query(Car).all()
    return templates.TemplateResponse("del_car.html", {"request": request, "cars": cars})
