"""API routes for the Maximo Risk Assessment Generator."""

from .workorder_routes import router as workorder_router
from .jha_routes import router as jha_router
from .health_routes import router as health_router

__all__ = [
    "workorder_router",
    "jha_router",
    "health_router",
]

# Made with Bob
