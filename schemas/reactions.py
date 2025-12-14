from pydantic import BaseModel
from typing import Dict

class ReactionCreate(BaseModel):
    emoji: str

class ReactionStats(BaseModel):
    emoji_counts: Dict[str, int]  # {"👀": 5, "👍": 3, ...}
    user_reactions: list[str]  # Emojis the current user has reacted with