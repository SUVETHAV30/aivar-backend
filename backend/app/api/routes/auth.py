from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.auth_service import AuthService
from app.services.logging_service import logger

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        logger.warning(
            "Failed login attempt - user not found",
            extra={"username": payload.username}
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    auth_svc = AuthService()
    if not auth_svc.verify_password(payload.password, user.hashed_password):
        logger.warning(
            "Failed login attempt - invalid password",
            extra={"username": payload.username}
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    token = auth_svc.create_token(user.username, role=user.role)
    logger.info(
        "Successful login",
        extra={"username": user.username, "role": user.role}
    )
    return TokenResponse(access_token=token, role=user.role)
