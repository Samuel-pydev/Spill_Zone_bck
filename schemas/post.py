from pydantic import BaseModel
from datetime import datetime

class FeedPostCreate(BaseModel):
    text: str

class FeedPostResponse(BaseModel):
    id: int
    user_id: int  # ADDED THIS LINE
    text: str
    timestamp: datetime
    
    class Config:
        from_attributes = True