# auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os, random, string

from . import models, schemas, database

# Load environment variables from .env
load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 Secrets from .env
SECRET_KEY = os.getenv("SECRET_KEY", "fallbacksecret")  # fallback if .env missing
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Optional helpers if you still keep classic accounts
def get_password_hash(password: str): return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str): return pwd_context.verify(plain_password, hashed_password)

def _random_guest_name():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"Guest_{suffix}"

def _ensure_unique_username(db: Session, base_name: str) -> str:
    name = base_name
    # If you have a unique constraint on username, ensure uniqueness
    while db.query(models.User).filter(models.User.username == name).first():
        name = _random_guest_name()
    return name

# === 🚀 Anonymous flow: create a guest and return a token ===
@router.post("/guest")
def create_guest(
    profile: schemas.GuestProfile | None = Body(None),
    db: Session = Depends(database.get_db)
):
    """
    Creates a temporary anonymous user and returns { access_token, token_type, user }.
    No email/password required.
    """
    # Generate a unique guest username
    username = _ensure_unique_username(db, _random_guest_name())

    new_user = models.User(
        username=username,
        email=None,         # Anonymous
        password=None,      # Anonymous
        age=getattr(profile, "age", None) if profile else None,
        gender=getattr(profile, "gender", None) if profile else None,
        location=getattr(profile, "location", None) if profile else None,
        interests=getattr(profile, "interests", None) if profile else None,
        language=getattr(profile, "language", None) if profile else None,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id), "role": "guest"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": schemas.UserOut.model_validate(new_user)
    }

# === (Optional) Keep classic signup/login (not required for guests) ===
@router.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    hashed_pw = get_password_hash(user.password)
    new_user = models.User(username=user.username, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or not user.password or not verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(data={"sub": str(user.id), "role": "user"})
    return {"access_token": token, "token_type": "bearer"}
