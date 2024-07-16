from fastapi import APIRouter, Request, Depends, responses, status
from fastapi.templating import Jinja2Templates
from app.models import User
from app.utils import hash_password
from app.db import get_session
from sqlmodel import Session, select
from jwt import decode
from app.config import SECRET_KEY, ALGORITHM


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


@router.get("/account")
def account(request: Request, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    if not token:
        errors.append("Войдите в аккаунт")
        return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            errors.append("Сначала создайте учетную запись или войдите в систему")
            return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})
        return templates.TemplateResponse("account.html", {"request": request, "user": user})


@router.get("/all_users")
def all_users(request: Request, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        users = db.query(User).all()
        return templates.TemplateResponse("all_users.html", {"request": request, "users": users})
    else:
        errors.append("Не вошли в аккаунт/Не являетесь администратором")
        return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})


@router.post("/all_users/{id}")
def all_users(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        errors.append("Войдите в аккаунт")
        return templates.TemplateResponse("all_users.html", {"request": request, "errors": errors})
    if role != "super_user":
        errors.append("Вы не являетесь администратором")
        return templates.TemplateResponse("all_users.html", {"request": request, "errors": errors})
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("all_users.html", {"request": request, "errors": errors})
    db.delete(user)
    db.commit()
    users = db.query(User).all()
    return templates.TemplateResponse("all_users.html", {"request": request, "users": users})


@router.get("/verify_user")
def verify_user(request: Request, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        users = db.query(User).filter(User.role == "no_verify").all()
        return templates.TemplateResponse("verify_user.html", {"request": request, "users": users})
    else:
        errors.append("Не вошли в аккаунт/Не являетесь администратором")
        return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})


@router.post("/verify_user/{id}")
def verify_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        errors.append("Войдите в аккаунт")
        return templates.TemplateResponse("verify_user.html", {"request": request, "errors": errors})
    if role != "super_user":
        errors.append("Вы не являетесь администратором")
        return templates.TemplateResponse("verify_user.html", {"request": request, "errors": errors})
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("verify_user.html", {"request": request, "errors": errors})
    user.verify_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    users = db.query(User).filter(User.role == "no_verify").all()
    return templates.TemplateResponse("verify_user.html", {"request": request, "users": users})


@router.get("/BAN_user")
def BAN_user(request: Request, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        users = db.query(User).all()
        return templates.TemplateResponse("BAN_user.html", {"request": request, "users": users})
    else:
        errors.append("Не вошли в аккаунт/Не являетесь администратором")
        return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})


@router.post("/BAN_user/{id}")
def BAN_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        errors.append("Войдите в аккаунт")
        return templates.TemplateResponse("BAN_user.html", {"request": request, "errors": errors})
    if role != "super_user":
        errors.append("Вы не являетесь администратором")
        return templates.TemplateResponse("BAN_user.html", {"request": request, "errors": errors})
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("BAN_user.html", {"request": request, "errors": errors})
    user.ban_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    users = db.query(User).all()
    return templates.TemplateResponse("BAN_user.html", {"request": request, "users": users})


@router.post("/un_BAN_user/{id}")
def un_BAN_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        errors.append("Войдите в аккаунт")
        return templates.TemplateResponse("BAN_user.html", {"request": request, "errors": errors})
    if role != "super_user":
        errors.append("Вы не являетесь администратором")
        return templates.TemplateResponse("BAN_user.html", {"request": request, "errors": errors})
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("BAN_user.html", {"request": request, "errors": errors})
    user.un_ban_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    users = db.query(User).all()
    return templates.TemplateResponse("BAN_user.html", {"request": request, "users": users})


@router.get("/make_super_user")
def make_super_user(request: Request, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        verify_users = db.query(User).filter(User.role == "verify").all()
        super_users = db.query(User).filter(User.role == "super_user").all()
        users = verify_users + super_users
        return templates.TemplateResponse("make_super_user.html", {"request": request, "users": users})
    else:
        errors.append("Не вошли в аккаунт/Не являетесь администратором")
        return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})


@router.post("/make_super_user/{id}")
def make_super_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        errors.append("Войдите в аккаунт")
        return templates.TemplateResponse("make_super_user.html", {"request": request, "errors": errors})
    if role != "super_user":
        errors.append("Вы не являетесь администратором")
        return templates.TemplateResponse("make_super_user.html", {"request": request, "errors": errors})
    user = db.exec(select(User).where(User.id == id)).first()
    user.super_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    verify_users = db.query(User).filter(User.role == "verify").all()
    super_users = db.query(User).filter(User.role == "super_user").all()
    users = verify_users + super_users
    return templates.TemplateResponse("make_super_user.html", {"request": request, "users": users})


@router.post("/un_make_super_user/{id}")
async def un_make_super_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        errors.append("Войдите в аккаунт")
        return templates.TemplateResponse("make_super_user.html", {"request": request, "errors": errors})
    if role != "super_user":
        errors.append("Вы не являетесь администратором")
        return templates.TemplateResponse("make_super_user.html", {"request": request, "errors": errors})
    user = db.exec(select(User).where(User.id == id)).first()
    user.un_super_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    verify_users = db.query(User).filter(User.role == "verify").all()
    super_users = db.query(User).filter(User.role == "super_user").all()
    users = verify_users + super_users
    return templates.TemplateResponse("make_super_user.html", {"request": request, "users": users})


@router.get("/update")
def update(request: Request, db: Session = Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    if token:
        return templates.TemplateResponse("update.html", {"request": request})
    else:
        errors.append("Не вошли в аккаунт/Не являетесь администратором")
        return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})


@router.post("/update")
async def update(request: Request, db: Session = Depends(get_session)):
    errors = []
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    complete_password = form.get("complete_password")
    token = request.cookies.get("access_token")
    if not token:
        errors.append("Не авторизовались")
        return templates.TemplateResponse("update.html", {"request": request, "errors": errors})
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        if user is None:
            errors.append("Cначала создайте учетную запись или войдите в систему")
            return templates.TemplateResponse("update.html", {"request": request, "errors": errors})
        if user.role == 'no_verify':
            errors.append("Вы не прошли проверку")
            return templates.TemplateResponse("update.html", {"request": request, "errors": errors})
        if password != complete_password:
            errors.append("Неверное повторение пароля")
            return templates.TemplateResponse("update.html", {"request": request, "errors": errors})
        if user.email != email:
            errors.append("Это не ваша почта")
            return templates.TemplateResponse("update.html", {"request": request, "errors": errors})
        user.hash_password = hash_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        msg = "Пароль изменен"
        return templates.TemplateResponse("update.html", {"request": request, "msg": msg})


@router.post("/get_all_users/xlsx")
def get_all_users_xlsx(request: Request, db: Session = Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    if token:
        name = "get_all_users"
        users = db.query(User).all()
        get_xlsx(users, f'{name}.xlsx')
        return FileResponse(path=f'{name}.xlsx', filename=f'{name}.xlsx', media_type='multipart/form-data')
    else:
        errors.append("Не вошли в аккаунт/Не являетесь администратором")
        return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})
