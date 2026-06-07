# main.py
# FastAPI app entry point.
# Sets up CORS, registers routes, and creates DB tables on startup.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router
from app.db.database import Base, engine
from app.db import models  # noqa - registers models with SQLAlchemy

app = FastAPI(title="Chat-AI API")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"status": "Chat-AI backend running"}