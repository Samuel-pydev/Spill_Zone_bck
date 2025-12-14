from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from database import Base

class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("feed_posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    emoji = Column(String)  # The emoji (👀, 👍, 💀, ☕)
    
    # Ensure one user can only react once per emoji per post
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', 'emoji', name='unique_user_post_emoji'),
    )