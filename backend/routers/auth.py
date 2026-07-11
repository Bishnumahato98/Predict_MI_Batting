"""Auth router — register, login, JWT tokens."""

import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

from db.mongo import users_col
from models.schemas import RegisterRequest, LoginRequest

load_dotenv()

router = APIRouter()

JWT_SECRET         = os.getenv("JWT_SECRET", "change_this_secret")
JWT_ALGORITHM      = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email   = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = users_col.find_one({"email": email}, {"password": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user["_id"] = str(user["_id"])
    return user


@router.post("/register")
def register(body: RegisterRequest):
    if users_col.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    users_col.insert_one({
        "name":       body.name,
        "email":      body.email,
        "password":   pwd_context.hash(body.password),
        "created_at": datetime.now(timezone.utc),
    })
    return {"success": True, "data": {"email": body.email}, "message": "Registered successfully"}


@router.post("/login")
def login(body: LoginRequest):
    user = users_col.find_one({"email": body.email})
    if not user or not pwd_context.verify(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(body.email)
    return {
        "success": True,
        "data": {
            "token": token,
            "user": {"name": user["name"], "email": user["email"]},
        },
        "message": "Login successful",
    }


@router.get("/whoami")
def whoami(user: dict = Depends(get_current_user)):
    return {"success": True, "data": user, "message": "Current user"}
