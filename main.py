from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base, get_db  
from routes import auth_router, feed_router, messages_router
from database import engine, Base
# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="SPILLZONE API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(messages_router)

from sqlalchemy import text
from sqlalchemy.orm import Session

@app.get("/migrate")
def migrate_database(db: Session = Depends(get_db)):
    try:
        # Add user_id column to feed_posts
        db.execute(text("ALTER TABLE feed_posts ADD COLUMN user_id INTEGER REFERENCES users(id)"))
        db.commit()
        return {"status": "Migration completed successfully"}
    except Exception as e:
        db.rollback()
        return {"status": "Migration failed", "error": str(e)}

@app.get("/")
def root():
    return {"message": "SPILLZONE API is running"}
