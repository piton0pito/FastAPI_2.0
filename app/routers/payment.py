from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import Car, User, Rent, Payment
from app.schemas import PaymentCreate
from app.utils import verify_access_token

router = APIRouter(tags=['payment'],
                   responses={404: {"description": "Not found"}})


@router.post('/make_payment/')
def make_payment(data: PaymentCreate, user: User = Depends(verify_access_token),
                 session: Session = Depends(get_session)):
    payment = session.exec(select(Payment).where(Payment.user_id == user.id).where(Payment.status == 'waiting')).first()
    if not payment:
        return "You don't have any unpaid trips"
    # списать деньги с карты клиента
    payment.payment()
    session.add(payment)
    session.commit()
    session.refresh(payment)
    raise HTTPException(status_code=200)


@router.get('/my_payment/')
def get_my_payment(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    payments = session.exec(select(Payment).where(Payment.user_id == user.id)).all()
    if not payments:
        return "You don't have any payments"
    return payments
