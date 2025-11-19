"""API v1 router combining all endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, players, teams

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(players.router, prefix="", tags=["Players"])
api_router.include_router(teams.router, prefix="", tags=["Teams"])
