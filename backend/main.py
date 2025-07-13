from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as api_router
from app.config.logging import setup_logging

app = FastAPI(
    title="RAG API",
    description="Backend for the RAG system",
    version="0.1.0"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # for the sake of dev, TODO: change to the frontend url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# API endpoints
app.include_router(api_router, prefix="/api/v1")

setup_logging()

@app.get("/")
async def root():
    return {"message": "Welcome! Rag is running :)"}