from fastapi import FastAPI

from backend.api.chat_api import router as chat_router


app = FastAPI(
    title="Source2Study API",
    description="AI-powered learning assistant API",
    version="1.0.0",
)


app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "Source2Study API is running."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }