from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/users")
def list_users():
    db: Session = SessionLocal()
    users = db.query(User).all()
    return [{"username": u.username, "role": u.role} for u in users]
