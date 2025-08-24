from fastapi import FastAPI
from app import models, database, auth, chat
from app.database import engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Sayonara Backend 🚀")

# Include authentication routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include chat routes (handles text + WebRTC signaling)
app.include_router(chat.router, prefix="/chat", tags=["chat"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Sayonara Backend Running 🚀"}
