from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    
    class Config:
        from_attributes = True