# pyrefly: ignore [missing-import]
from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


# Creates the FastAPI app and attaches all routes.
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Grounded Python Q&A API backed by Stack Overflow-style retrieval.",
    )
    app.include_router(router)
    return app


app = create_app()
