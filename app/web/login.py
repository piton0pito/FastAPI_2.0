from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from app.utils import create_access_token

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    errors = []
    if len(password) < 6:
        errors.append("Пароль должен состоять от 6 и более символов!")
        return templates.TemplateResponse("login.html", {"request": request, "errors": errors})

    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not user.verify_password(password):
        errors.append("Неверны почта или пароль!")
        return templates.TemplateResponse("login.html", {"request": request, "errors": errors})
    else:
        access_token = create_access_token(data={"sub": user.id})
        msg = "Вход выполнен!"
        response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response


