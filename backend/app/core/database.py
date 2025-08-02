from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Use the dynamic database URL
DATABASE_URL = settings.get_database_url

engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False}
        if "sqlite" in DATABASE_URL
        else {}
    ),
    # PostgreSQL specific optimizations
    pool_pre_ping=True if "postgresql" in DATABASE_URL else False,
    pool_recycle=300 if "postgresql" in DATABASE_URL else -1,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
