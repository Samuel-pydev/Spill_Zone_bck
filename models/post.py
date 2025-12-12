from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base

class FeedPost(Base):
    __tablename__ = "feed_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Add this
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
