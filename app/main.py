import uvicorn
from fastapi import FastAPI,HTTPException
from app.db import engine
from app.routers import user, car_and_rent, payment, admin
from sqlmodel import SQLModel

SQLModel.metadata.create_all(engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(car_and_rent.router)
app.include_router(payment.router)
app.include_router(admin.router)


@app.get('/mem/')
def get():
    raise HTTPException(status_code=418)


uvicorn.run(app, port=8001)