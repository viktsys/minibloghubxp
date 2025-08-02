from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


class PostService:
    
    @staticmethod
    def get_posts(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        author_id: Optional[int] = None,
        is_active: bool = True
    ) -> List[Post]:
        """Get posts with pagination and filters"""
        query = db.query(Post).filter(Post.is_active == is_active)
        
        if author_id:
            query = query.filter(Post.author_id == author_id)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_post(db: Session, post_id: int) -> Optional[Post]:
        """Get a specific post by ID"""
        return db.query(Post).filter(
            and_(Post.id == post_id, Post.is_active.is_(True))
        ).first()
    
    @staticmethod
    def create_post(db: Session, post: PostCreate, author_id: int) -> Post:
        """Create a new post"""
        db_post = Post(
            **post.dict(),
            author_id=author_id
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    
    @staticmethod
    def update_post(
        db: Session,
        post_id: int,
        post_update: PostUpdate,
        author_id: int
    ) -> Optional[Post]:
        """Update a post"""
        db_post = db.query(Post).filter(
            and_(
                Post.id == post_id,
                Post.author_id == author_id,
                Post.is_active.is_(True)
            )
        ).first()
        
        if not db_post:
            return None
            
        update_data = post_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_post, field, value)
            
        db.commit()
        db.refresh(db_post)
        return db_post
    
    @staticmethod
    def delete_post(db: Session, post_id: int, author_id: int) -> bool:
        """Soft delete a post"""
        db_post = db.query(Post).filter(
            and_(
                Post.id == post_id,
                Post.author_id == author_id,
                Post.is_active.is_(True)
            )
        ).first()
        
        if not db_post:
            return False
            
        db_post.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def create_imported_post(
        db: Session, 
        title: str, 
        content: str, 
        author_id: int,
        external_id: int
    ) -> Post:
        """Create a post imported from external source"""
        # Check if post already exists
        existing = db.query(Post).filter(
            and_(
                Post.external_id == external_id,
                Post.is_imported.is_(True)
            )
        ).first()
        
        if existing:
            return existing
            
        db_post = Post(
            title=title,
            content=content,
            author_id=author_id,
            external_id=external_id,
            is_imported=True
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post


post_service = PostService()
