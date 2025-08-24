from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --------------------
# User Schemas
# --------------------
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    interests: Optional[str] = None
    language: Optional[str] = None

class UserCreate(UserBase):
    username: str
    email: Optional[str] = None
    password: str

class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

# Used by /auth/login
class LoginRequest(BaseModel):
    username: str
    password: str

# Used by /auth/guest
class GuestProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    interests: Optional[str] = None
    language: Optional[str] = None

# --------------------
# Match Schemas
# --------------------
class MatchBase(BaseModel):
    user1_id: int
    user2_id: int

class MatchOut(MatchBase):
    id: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    class Config:
        orm_mode = True

# --------------------
# Report Schemas
# --------------------
class ReportBase(BaseModel):
    reporter_id: int
    reported_id: int
    reason: str

class ReportOut(ReportBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

# --------------------
# Friend Schemas
# --------------------
class FriendBase(BaseModel):
    user_id: int
    friend_id: int

class FriendOut(FriendBase):
    id: int
    status: str
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True
