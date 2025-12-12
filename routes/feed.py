from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, FeedPost
from schemas import FeedPostCreate, FeedPostResponse
from utils import get_current_user

router = APIRouter(prefix="/feed", tags=["feed"])

@router.post("", response_model=FeedPostResponse)
def create_feed_post(
    post: FeedPostCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    new_post = FeedPost(text=post.text, user_id=current_user.id)  # ADDED user_id
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("", response_model=List[FeedPostResponse])
def get_feed(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    posts = db.query(FeedPost).order_by(FeedPost.timestamp.desc()).all()
    return posts

# ADDED THIS ENDPOINT
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(FeedPost).filter(FeedPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Only owner can delete
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