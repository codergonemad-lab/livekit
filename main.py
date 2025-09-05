from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import os
from dotenv import load_dotenv

# Import our modules
from database import get_db, create_tables, User, Room, RoomMembership
from schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    RoomCreate, RoomResponse, RoomWithParticipants,
    TokenRequest, TokenResponse
)
from auth import (
    authenticate_user, create_access_token, get_current_user,
    get_password_hash
)
from livekit_service import livekit_service

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="LiveKit Video Calling Backend",
    description="Backend API for video calling app with LiveKit integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "livekit-video-calling-backend"}

# === USER MANAGEMENT ENDPOINTS ===

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active,
        created_at=db_user.created_at
    )

@app.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

# === ROOM MANAGEMENT ENDPOINTS ===

@app.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room: RoomCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new room."""
    # Check if room with this name already exists
    existing_room = db.query(Room).filter(Room.name == room.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with this name already exists"
        )
    
    # Create room in database
    db_room = Room(
        name=room.name,
        display_name=room.display_name,
        description=room.description,
        creator_id=current_user.id,
        max_participants=room.max_participants
    )
    
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    
    # Create room on LiveKit server
    await livekit_service.create_room(room.name, room.max_participants)
    
    return RoomResponse(
        id=db_room.id,
        name=db_room.name,
        display_name=db_room.display_name,
        description=db_room.description,
        creator_id=db_room.creator_id,
        is_active=db_room.is_active,
        max_participants=db_room.max_participants,
        created_at=db_room.created_at,
        participant_count=0
    )

@app.get("/rooms", response_model=List[RoomResponse])
async def list_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all active rooms."""
    rooms = db.query(Room).filter(Room.is_active == True).all()
    
    room_responses = []
    for room in rooms:
        # Count active participants
        participant_count = db.query(RoomMembership).filter(
            RoomMembership.room_id == room.id,
            RoomMembership.is_active == True
        ).count()
        
        room_responses.append(RoomResponse(
            id=room.id,
            name=room.name,
            display_name=room.display_name,
            description=room.description,
            creator_id=room.creator_id,
            is_active=room.is_active,
            max_participants=room.max_participants,
            created_at=room.created_at,
            participant_count=participant_count
        ))
    
    return room_responses

@app.get("/rooms/{room_id}", response_model=RoomWithParticipants)
async def get_room_details(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get room details including participants."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Get participants from LiveKit
    room_info = await livekit_service.get_room_info(room.name)
    participants = []
    
    if room_info and room_info.get("participants"):
        for p in room_info["participants"]:
            participants.append({
                "identity": p.identity,
                "name": p.name,
                "metadata": p.metadata,
                "num_tracks": len(p.tracks),
                "permission": {
                    "can_publish": p.permission.can_publish,
                    "can_subscribe": p.permission.can_subscribe,
                    "can_publish_data": p.permission.can_publish_data
                }
            })
    
    return RoomWithParticipants(
        id=room.id,
        name=room.name,
        display_name=room.display_name,
        description=room.description,
        creator_id=room.creator_id,
        is_active=room.is_active,
        max_participants=room.max_participants,
        created_at=room.created_at,
        participant_count=len(participants),
        participants=participants
    )

@app.post("/rooms/{room_id}/join", response_model=TokenResponse)
async def join_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a room and get LiveKit access token."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if user is already in the room
    existing_membership = db.query(RoomMembership).filter(
        RoomMembership.user_id == current_user.id,
        RoomMembership.room_id == room_id,
        RoomMembership.is_active == True
    ).first()
    
    if not existing_membership:
        # Add user to room membership
        membership = RoomMembership(
            user_id=current_user.id,
            room_id=room_id
        )
        db.add(membership)
        db.commit()
    
    # Generate LiveKit access token
    token = livekit_service.create_access_token(
        room_name=room.name,
        participant_identity=str(current_user.id),
        participant_name=current_user.username,
        metadata=f"user_id:{current_user.id}"
    )
    
    return TokenResponse(
        token=token,
        room_name=room.name,
        participant_identity=str(current_user.id),
        livekit_url=livekit_service.livekit_url
    )

@app.post("/rooms/{room_id}/leave")
async def leave_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave a room."""
    membership = db.query(RoomMembership).filter(
        RoomMembership.user_id == current_user.id,
        RoomMembership.room_id == room_id,
        RoomMembership.is_active == True
    ).first()
    
    if membership:
        membership.is_active = False
        membership.left_at = db.execute("SELECT NOW()").scalar()
        db.commit()
    
    return {"message": "Left room successfully"}

@app.delete("/rooms/{room_id}")
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a room (only room creator can delete)."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    if room.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only room creator can delete the room"
        )
    
    # Mark room as inactive
    room.is_active = False
    
    # Mark all memberships as inactive
    memberships = db.query(RoomMembership).filter(RoomMembership.room_id == room_id).all()
    for membership in memberships:
        membership.is_active = False
    
    db.commit()
    
    # Delete room from LiveKit server
    await livekit_service.delete_room(room.name)
    
    return {"message": "Room deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
