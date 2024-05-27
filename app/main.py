import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks

from app.db import engine
from app.routers import user, car_and_rent, payment, admin
from sqlmodel import SQLModel

from app.utils import send_mail

SQLModel.metadata.create_all(engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(car_and_rent.router)
app.include_router(payment.router)
app.include_router(admin.router)


@app.get('/mem/')
def get():
    raise HTTPException(status_code=418)

@app.post("/send-email")
def schedule_mail(email: str, code: str, tasks: BackgroundTasks):
    send_mail(email, code)
    raise HTTPException(status_code=200, detail='Email has been scheduled')


uvicorn.run(app, port=8001)