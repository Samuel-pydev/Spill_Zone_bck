from pydantic import BaseModel
from datetime import datetime
from typing import Optional 

class FeedPostCreate(BaseModel):
    text: str

class FeedPostResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    text: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
