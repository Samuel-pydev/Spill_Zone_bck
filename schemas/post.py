from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class FeedPostCreate(BaseModel):
    text: str
    
    @field_validator('text')
    def validate_text_length(cls, v):
        if len(v) > 500:
            raise ValueError('Post cannot exceed 500 characters')
        if len(v.strip()) == 0:
            raise ValueError('Post cannot be empty')
        return v

class FeedPostResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    text: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
