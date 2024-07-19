import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.security import HTTPBasic
from fastapi.testclient import TestClient
from pathlib import Path

from sqlmodel import create_engine

from app.db import engine, get_session
from app.routers import user, car_and_rent, payment, admin
from sqlmodel import SQLModel, Session

from app.routers.admin import create_admin
from app.utils import send_mail, get_meme

from app.web import cars as web_cars
from app.web import users as web_users
from app.web import login as web_login
if __name__ == '__main__':
    SQLModel.metadata.create_all(engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(car_and_rent.router)
app.include_router(payment.router)
app.include_router(admin.router)
app.include_router(web_cars.router)
app.include_router(web_users.router)
app.include_router(web_login.router)


@app.get('/mem/')
def get():
    raise HTTPException(status_code=418)

@app.post("/send-email")
def schedule_mail(email: str, code: str, tasks: BackgroundTasks):
    send_mail(email, code)
    raise HTTPException(status_code=200, detail='Email has been scheduled')

@app.get("/random_meme")
async def get_image():
    await get_meme()
    image_path = Path("meme.jpg")  # Replace with the actual image path
    return FileResponse(image_path, media_type="image/jpeg")

if __name__ == '__main__':
    uvicorn.run(app, port=8001)
