from fastapi import APIRouter

router = APIRouter()

from .routes import images, models, vision

__all__ = ["router"] 