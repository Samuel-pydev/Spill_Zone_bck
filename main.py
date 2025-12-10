# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./spillzone.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security setup

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class FeedPost(Base):
    __tablename__ = "feed_posts"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    is_anonymous = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FeedPostCreate(BaseModel):
    text: str

class FeedPostResponse(BaseModel):
    id: int
    text: str
    timestamp: datetime

class MessageCreate(BaseModel):
    recipient_username: str
    text: str
    is_anonymous: bool = True

class MessageResponse(BaseModel):
    id: int
    text: str
    sender_username: Optional[str]
    is_anonymous: bool
    timestamp: datetime

# FastAPI app
app = FastAPI(title="SPILLZONE API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes
@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user/{username}")
def check_username(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return {"exists": True, "username": username}
    return {"exists": False}

@app.post("/feed", response_model=FeedPostResponse)
def create_feed_post(post: FeedPostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_post = FeedPost(text=post.text)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/feed", response_model=List[FeedPostResponse])
def get_feed(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    posts = db.query(FeedPost).order_by(FeedPost.timestamp.desc()).all()
    return posts

@app.post("/message")
def send_message(message: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if recipient exists
    recipient = db.query(User).filter(User.username == message.recipient_username).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create message
    new_message = Message(
        sender_id=None if message.is_anonymous else current_user.id,
        recipient_id=recipient.id,
        text=message.text,
        is_anonymous=message.is_anonymous
    )
    db.add(new_message)
    db.commit()
    return {"status": "sent"}

@app.get("/inbox", response_model=List[MessageResponse])
def get_inbox(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.recipient_id == current_user.id).order_by(Message.timestamp.desc()).all()
    
    result = []
    for msg in messages:
        sender_username = None
        if not msg.is_anonymous and msg.sender_id:
            sender = db.query(User).filter(User.id == msg.sender_id).first()
            sender_username = sender.username if sender else None
        
        result.append({
            "id": msg.id,
            "text": msg.text,
            "sender_username": sender_username,
            "is_anonymous": msg.is_anonymous,
            "timestamp": msg.timestamp
        })
    
    return result

@app.get("/")
def root():
    return {"message": "SPILLZONE API is running"}

# To run: uvicorn main:app --reload