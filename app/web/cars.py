from fastapi import APIRouter, Request, Depends, responses, status
from fastapi.templating import Jinja2Templates
from app.models import Car, User, Payment
from sqlmodel import Session, select
from app.db import get_session
from app.utils import verify_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/")
def home(request: Request, db: Session=Depends(get_session)):
    cars = db.query(Car).all()
    return templates.TemplateResponse("homepage.html", {"request": request, "cars": cars})


@router.get("/detail/{id}")
def car_detail(request: Request, id: int, db: Session=Depends(get_session)):
    car = db.query(Car).filter(Car.id == id).first()
    return templates.TemplateResponse(
        "car_detail.html", {"request": request, "car": car}
    )


@router.get("/payments")
def payments(request: Request):
    return templates.TemplateResponse("payments.html", {"request": request})


@router.post("/payments")
async def payments(request: Request, user: User=Depends(verify_access_token), db: Session=Depends(get_session)):
    form = await request.form()
    card_number = form.get("card_number")
    valid_thru_m = form.get("valid_thru_m")
    valid_thru_y = form.get("valid_thru_y")
    svv = form.get("svv")
    errors = []
    payment = db.exec(select(Payment).where(Payment.user_id == user.id).where(Payment.status == "waiting")).first()
    token = request.cookies.get("access_token")
    user = verify_access_token(token)
    if not user:
        errors.append("Пожалуйста, сначала войдите в систему")
        return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
    if not payment:
        errors.append("У вас нет неоплаченных поездок")
        return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
    if len(card_number) != 16:
        errors.append("Номер карты содержит 16 символов")
        return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
    if len(valid_thru_m) != 2:
        errors.append("Должно быть 2 символа")
        return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
    if len(valid_thru_y) != 2:
        errors.append("Должно быть 2 символа")
        return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
    if len(svv) != 3:
        errors.append("Должно быть 3 символа")
        return templates.TemplateResponse("payments.html", {"request": request, "errors": errors})
    payment.payment()
    db.add(payment)
    db.commit()
    db.refresh(payment)
    msg = "Вход выполнен!"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    return response


@router.get("/start_rent")
def start_rent(request: Request):
    return templates.TemplateResponse("start_rent.html", {"request": request})

@router.post("/start_rent")
async def start_rent(request: Request, db: Session=Depends(get_session)):
    form = await request.form()
    car_number = form.get("card_number")
    car = db.query(Car).filter(Car.car_number == car_number).first()
    errors = []
    if car:
        errors.append("Машина занята")
        return templates.TemplateResponse("start_rent.html", {"request": request, "errors": errors})
    return responses.RedirectResponse("/end_rent", status_code=status.HTTP_302_FOUND)



@router.get("/end_rent")
def end_rent(request: Request):
    return templates.TemplateResponse("end_rent.html", {"request": request})


@router.post("/end_rent")
async def end_rent(request: Request, db: Session=Depends(get_session)):
    form = await request.form()
    car_number = form.get("card_number")
    errors = []
    car = db.query(Car).filter(Car.car_number == car_number).first()
    if car:
        errors.append("Неправильный номер")
        return templates.TemplateResponse("end_rent.html", {"request": request, "errors": errors})
    return responses.RedirectResponse("/start_rent", status_code=status.HTTP_302_FOUND)
