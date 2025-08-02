from decouple import config


class Settings:
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-for-jwt")
    DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./blog.db")
    
    # PostgreSQL specific settings
    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="password")
    POSTGRES_HOST: str = config("POSTGRES_HOST", default="localhost")
    POSTGRES_PORT: str = config("POSTGRES_PORT", default="5432")
    POSTGRES_DB: str = config("POSTGRES_DB", default="minibloghub")
    
    UNSPLASH_ACCESS_KEY: str = config("UNSPLASH_ACCESS_KEY", default="")
    UNSPLASH_SECRET_KEY: str = config("UNSPLASH_SECRET_KEY", default="")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int
    )
    ALGORITHM: str = config("ALGORITHM", default="HS256")

    # CORS
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    PAGINATION_QUERY_PARAM: str = "page_size"
    PAGINATION_PAGE_PARAM: str = "page"
    PAGINATION_DEFAULT_PAGE: int = 1

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def get_database_url(self) -> str:
        """
        Get the appropriate database URL based on environment.
        If DATABASE_URL is provided, use it. Otherwise, construct
        PostgreSQL URL from components.
        """
        if self.DATABASE_URL != "sqlite:///./blog.db":
            return self.DATABASE_URL
        
        # If in production (DEBUG=False), use PostgreSQL
        if not self.DEBUG:
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )
        
        # Default to SQLite for development
        return self.DATABASE_URL


settings = Settings()
