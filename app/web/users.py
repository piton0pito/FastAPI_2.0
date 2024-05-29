from fastapi import APIRouter, Request, Depends, responses, status
from fastapi.templating import Jinja2Templates
from app.models import User
from app.utils import hash_password
from app.db import get_session
from sqlmodel import Session, select

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/register")
def reg(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def reg(request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    email = form.get("email")
    first_name = form.get("first_name")
    last_name = form.get("last_name")
    surname = form.get("surname")
    license = form.get("license")
    password = form.get("password")
    complete_password = form.get("complete_password")
    errors = []

    if len(password) < 6:
        errors.append("Пароль должен состоять от 6 и более символов!")
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})
    if (password != complete_password) or (len(password) != len(complete_password)):
        errors.append("Неверное повторение пароля!")
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})
    if len(license) != 10:
        errors.append("Лицензия должна состоять из 10 символов!")
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})

    user = User(email=email,
                hash_password=hash_password(password=password),
                first_name=first_name,
                last_name=last_name,
                surname=surname,
                license=license
                )

    duplicate_email = db.exec(select(User).where(User.email == email)).first()
    if duplicate_email:
        errors.append("Почта уже существует!")
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})
    duplicate_license = db.exec(select(User).where(User.license == license)).first()
    if duplicate_license:
        errors.append("Лицензия уже существует!")
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})

    db.add(user)
    db.commit()
    db.refresh(user)
    return responses.RedirectResponse(
        "/?msg=Вы зарегистрированы!", status_code=status.HTTP_302_FOUND
    )
