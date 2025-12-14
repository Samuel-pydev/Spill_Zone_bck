from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models import User, FeedPost, Reaction
from schemas import FeedPostCreate, FeedPostResponse
from utils import get_current_user

router = APIRouter(prefix="/feed", tags=["feed"])

@router.post("", response_model=FeedPostResponse)
def create_feed_post(
    post: FeedPostCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    new_post = FeedPost(text=post.text, user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return {
        **new_post.__dict__,
        "reaction_counts": {},
        "user_reactions": []
    }

@router.get("", response_model=List[FeedPostResponse])
def get_feed(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    posts = db.query(FeedPost).order_by(FeedPost.timestamp.desc()).all()
    
    result = []
    for post in posts:
        # Get reaction counts
        reactions = db.query(
            Reaction.emoji, 
            func.count(Reaction.id).label('count')
        ).filter(Reaction.post_id == post.id).group_by(Reaction.emoji).all()
        
        reaction_counts = {emoji: count for emoji, count in reactions}
        
        # Get current user's reactions
        user_reactions = db.query(Reaction.emoji).filter(
            Reaction.post_id == post.id,
            Reaction.user_id == current_user.id
        ).all()
        user_reactions = [r[0] for r in user_reactions]
        
        result.append({
            **post.__dict__,
            "reaction_counts": reaction_counts,
            "user_reactions": user_reactions
        })
    
    return result

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(FeedPost).filter(FeedPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    return {"status": "deleted"}

@router.post("", response_model=FeedPostResponse)
def create_feed_post(
    post: FeedPostCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    new_post = FeedPost(text=post.text, user_id=current_user.id)  # Add user_id
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post