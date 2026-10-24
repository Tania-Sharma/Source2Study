import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database.db import init_db
from backend.api.chat_api import router as chat_router
from backend.api.learning_api import router as learning_router
from backend.api.resource_api import router as resource_router
from backend.question_bank.api import router as question_bank_router


# Initialize database tables
try:
    init_db()
except Exception as e:
    print(f"Database initialization warning: {e}")

app = FastAPI(
    title="Source2Study API",
    description="AI-powered learning assistant and unified question bank API",
    version="2.0.0",
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)
app.include_router(learning_router)
app.include_router(resource_router)
app.include_router(question_bank_router)


# Mount built frontend if available
FRONTEND_DIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend",
    "dist",
)

if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/app", include_in_schema=False)
    @app.get("/app/{full_path:path}", include_in_schema=False)
    def serve_frontend_app(full_path: str = ""):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))


@app.get("/")
def root():
    return {
        "message": "Source2Study API is running.",
        "version": "2.0.0",
        "frontend_url": "/app",
        "docs_url": "/docs",
        "endpoints": {
            "chat": "/chat",
            "learning": [
                "/ai/summarize",
                "/ai/explain",
                "/quiz/generate",
                "/quiz/mcq",
                "/quiz/evaluate",
            ],
            "resources": "/resources",
            "question_bank": "/question-bank",
        },
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Source2Study",
    }
