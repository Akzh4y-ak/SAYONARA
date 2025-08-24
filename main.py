from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database, auth
from app.video_chat import router as video_router
from app.database import engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Sayonara Backend 🚀")

# CORS settings
origins = [
    "http://localhost:5173",
    "https://sayonara-frontend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(video_router, prefix="", tags=["video-chat"])  # ✅ no prefix for WebSocket

# Root endpoint
@app.get("/")
def root():
    return {"message": "Sayonara Backend Running 🚀"}
