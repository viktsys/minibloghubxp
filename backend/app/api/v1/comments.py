from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import (
    Comment as CommentSchema, CommentCreate, CommentUpdate
)

router = APIRouter()


@router.get("/{post_id}/comments/", response_model=List[CommentSchema])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    """Get all comments for a post"""
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    comments = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.is_active.is_(True)
    ).all()
    
    return comments


@router.post("/{post_id}/comments/", response_model=CommentSchema)
def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new comment"""
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db_comment = Comment(
        content=comment.content,
        post_id=post_id,
        author_id=current_user.id
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


@router.put("/comments/{comment_id}", response_model=CommentSchema)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a comment"""
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.author_id == current_user.id,
        Comment.is_active.is_(True)
    ).first()
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or no permission to update"
        )
    
    if comment_update.content is not None:
        db_comment.content = comment_update.content
    
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment"""
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.author_id == current_user.id,
        Comment.is_active.is_(True)
    ).first()
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or no permission to delete"
        )
    
    db_comment.is_active = False
    db.commit()
    
    return {"message": "Comment deleted successfully"}
