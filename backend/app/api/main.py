from fastapi import APIRouter

from app.api.routes import rag, user

api_router = APIRouter()
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
