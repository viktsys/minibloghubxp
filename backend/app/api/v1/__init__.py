from fastapi import APIRouter
from .auth import router as auth_router
from .posts import router as posts_router
from .comments import router as comments_router
from .images import router as images_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(posts_router, prefix="/posts", tags=["posts"])
api_router.include_router(comments_router, prefix="/posts", tags=["comments"])
api_router.include_router(images_router, prefix="/images", tags=["images"])
