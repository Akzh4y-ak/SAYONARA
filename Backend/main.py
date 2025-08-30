from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app import models, database, auth
from app.video_chat import router as video_router
from app.database import engine

# Create database tables
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating database tables: {e}")

# Initialize FastAPI app
app = FastAPI(title="Sayonara Backend 🚀")

# CORS settings
origins = [
    "http://localhost:5173",
    "https://sayonara-frontend.onrender.com",
    "https://sayonara-frontend1.onrender.com",
    "*"  # <-- Add the wildcard here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # <-- This is the only place it should be defined
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(video_router, prefix="/ws-video", tags=["video-chat"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Sayonara Backend Running 🚀"}

# Example error handling for a sample endpoint
@app.get("/example")
def example_endpoint():
    try:
        # Your logic here
        return {"message": "This is an example endpoint."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))