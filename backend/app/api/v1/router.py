"""
API v1 Router Configuration
Aggregates all v1 endpoints into a single router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import players, health

# Create API v1 router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    players.router,
    prefix="/players",
    tags=["players"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)