from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Message
from schemas import MessageCreate, MessageResponse
from utils import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/send")
def send_message(
    message: MessageCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
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

@router.get("/inbox", response_model=List[MessageResponse])
def get_inbox(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    messages = db.query(Message).filter(
        Message.recipient_id == current_user.id
    ).order_by(Message.timestamp.desc()).all()
    
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