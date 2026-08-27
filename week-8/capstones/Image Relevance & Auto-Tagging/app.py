from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from src.routes.ai import router as ai_router

load_dotenv()

app = FastAPI(
    title="FlyRank Week 7 - Put an LLM Behind Your API",
    version="1.0.0",
    description="A trustworthy single-purpose LLM API with validation, repair, timeout, retries, cost logging and a kill switch.",
)

app.include_router(ai_router)


@app.get("/")
def home():
    return {
        "message": "Week 7 LLM API is running",
        "docs": "/docs",
        "endpoint": "POST /triage",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
