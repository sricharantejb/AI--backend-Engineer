from fastapi import FastAPI
from src.routes.ai import router as ai_router

app = FastAPI(
    title="LLM Support Ticket API",
    description="AI-powered support ticket classification API",
    version="1.0.0"
)

app.include_router(ai_router)


@app.get("/")
def home():
    return {
        "message": "LLM API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }