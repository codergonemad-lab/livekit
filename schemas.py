from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

# Room Schemas
class RoomBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    max_participants: Optional[int] = 50

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoomResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    creator_id: int
    is_active: bool
    max_participants: int
    created_at: datetime
    participant_count: Optional[int] = 0

class RoomParticipant(BaseModel):
    identity: str
    name: str
    metadata: str
    num_tracks: int
    permission: dict

class RoomWithParticipants(RoomResponse):
    participants: List[RoomParticipant] = []

# Token Schemas
class TokenRequest(BaseModel):
    room_name: str
    participant_name: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    room_name: str
    participant_identity: str
    livekit_url: str

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
