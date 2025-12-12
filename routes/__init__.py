from routes.auth import router as auth_router
from routes.feed import router as feed_router
from routes.messages import router as messages_router

__all__ = ["auth_router", "feed_router", "messages_router"]