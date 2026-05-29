from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat_routes, mcq_routes, summary_routes, upload_routes
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="RAG study assistant: PDF upload, Q&A, summary, MCQ generation.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(upload_routes.router)
    app.include_router(chat_routes.router)
    app.include_router(summary_routes.router)
    app.include_router(mcq_routes.router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "Personalized Learning Assistant API is running"}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
