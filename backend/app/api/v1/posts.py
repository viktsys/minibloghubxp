from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.post import Post, PostCreate, PostUpdate
from app.services.post_service import post_service
from app.services.jsonplaceholder_service import jsonplaceholder_service

router = APIRouter()


@router.get("/", response_model=List[Post])
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    author_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all posts with pagination"""
    posts = post_service.get_posts(
        db=db,
        skip=skip,
        limit=limit,
        author_id=author_id
    )
    return posts


@router.get("/{post_id}", response_model=Post)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post"""
    post = post_service.get_post(db=db, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post


@router.post("/", response_model=Post)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new post"""
    return post_service.create_post(
        db=db,
        post=post,
        author_id=current_user.id
    )


@router.put("/{post_id}", response_model=Post)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a post"""
    updated_post = post_service.update_post(
        db=db,
        post_id=post_id,
        post_update=post_update,
        author_id=current_user.id
    )
    
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to update it"
        )
    
    return updated_post


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a post"""
    success = post_service.delete_post(
        db=db,
        post_id=post_id,
        author_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    
    return {"message": "Post deleted successfully"}


@router.post("/import/")
def import_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import posts from JSONPlaceholder"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can import posts"
        )
    
    try:
        external_posts = jsonplaceholder_service.get_posts()
        imported_count = 0
        
        for ext_post in external_posts:
            post_service.create_imported_post(
                db=db,
                title=ext_post["title"],
                content=ext_post["body"],
                author_id=current_user.id,
                external_id=ext_post["id"]
            )
            imported_count += 1
        
        return {
            "message": f"Successfully imported {imported_count} posts",
            "count": imported_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing posts: {str(e)}"
        )
