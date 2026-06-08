# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.routes.upload import router as upload_router      # new
from app.db.database import Base, engine
from app.db import models  # noqa

app = FastAPI(title="Chat-AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Register both routers
app.include_router(chat_router, prefix="/api")
app.include_router(upload_router, prefix="/api")         # new

@app.get("/")
def root():
    return {"status": "Chat-AI backend running"}