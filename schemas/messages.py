from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    recipient_username: str
    text: str
    is_anonymous: bool = True
    
    @field_validator('text')
    def validate_text_length(cls, v):
        if len(v) > 1000:
            raise ValueError('Message cannot exceed 1000 characters')
        if len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        return v

class MessageResponse(BaseModel):
    id: int
    text: str
    sender_username: Optional[str]
    is_anonymous: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True
