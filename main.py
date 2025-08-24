from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database, auth
# from app import chat   # ⛔ disabled for now
from app.database import engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Sayonara Backend 🚀")

# Allow frontend to connect (CORS)
origins = [
    "http://localhost:5173",  # vite local dev
    "https://sayonara-frontend.onrender.com",  # deployed frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# ⛔ Temporarily disabled
# app.include_router(chat.router, prefix="/chat", tags=["chat"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Sayonara Backend Running 🚀"}
