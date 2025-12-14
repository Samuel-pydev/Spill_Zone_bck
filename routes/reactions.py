from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Reaction
from schemas import ReactionCreate
from utils import get_current_user

router = APIRouter(prefix="/reactions", tags=["reactions"])

ALLOWED_EMOJIS = ["👀", "👍", "💀", "☕"]

@router.post("/post/{post_id}")
def toggle_reaction(
    post_id: int,
    reaction: ReactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate emoji
    if reaction.emoji not in ALLOWED_EMOJIS:
        raise HTTPException(status_code=400, detail="Invalid emoji")
    
    # Check if reaction exists
    existing = db.query(Reaction).filter(
        Reaction.post_id == post_id,
        Reaction.user_id == current_user.id,
        Reaction.emoji == reaction.emoji
    ).first()
    
    if existing:
        # Remove reaction (toggle off)
        db.delete(existing)
        db.commit()
        return {"status": "removed"}
    else:
        # Add reaction (toggle on)
        new_reaction = Reaction(
            post_id=post_id,
            user_id=current_user.id,
            emoji=reaction.emoji
        )
        db.add(new_reaction)
        db.commit()
        return {"status": "added"}