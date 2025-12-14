from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
from routes import auth_router, feed_router, messages_router, reactions_router
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
app.include_router(reactions_router) 

@app.get("/")
def root():
    return {"message": "SPILLZONE API is running"}
