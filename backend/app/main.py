from fastapi import FastAPI

from .routers import players


def create_app() -> FastAPI:
    """Application factory for the FPL Optimizer API."""
    app = FastAPI(title="FPL Optimizer API")
    app.include_router(players.router)
    return app


app = create_app()