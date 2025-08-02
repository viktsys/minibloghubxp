#!/usr/bin/env python3
"""
Database setup and migration script for Mini Blog Hub XP
"""
import sys
from pathlib import Path

import typer
from sqlalchemy import text

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings  # noqa: E402
from app.core.database import engine, Base  # noqa: E402

app = typer.Typer()


@app.command()
def create_db():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        typer.echo("✅ Database tables created successfully!")
    except Exception as e:
        typer.echo(f"❌ Error creating database tables: {e}")
        raise typer.Exit(1)


@app.command()
def check_connection():
    """Check database connection"""
    try:
        with engine.connect() as conn:
            if "postgresql" in settings.get_database_url:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                typer.echo("✅ PostgreSQL connection successful!")
                typer.echo(f"Database version: {version}")
            else:
                result = conn.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                typer.echo("✅ SQLite connection successful!")
                typer.echo(f"SQLite version: {version}")
    except Exception as e:
        typer.echo(f"❌ Database connection failed: {e}")
        raise typer.Exit(1)


@app.command()
def show_config():
    """Show current database configuration"""
    db_url = settings.get_database_url
    typer.echo("📋 Current Database Configuration:")
    typer.echo(f"DEBUG mode: {settings.DEBUG}")
    typer.echo(f"Database URL: {db_url}")
    
    if "postgresql" in db_url:
        typer.echo("Database type: PostgreSQL")
        typer.echo(f"Host: {settings.POSTGRES_HOST}")
        typer.echo(f"Port: {settings.POSTGRES_PORT}")
        typer.echo(f"Database: {settings.POSTGRES_DB}")
        typer.echo(f"User: {settings.POSTGRES_USER}")
    else:
        typer.echo("Database type: SQLite")


@app.command()
def reset_db():
    """Reset database (DROP and CREATE all tables)"""
    confirm = typer.confirm("⚠️  This will DELETE ALL DATA! Are you sure?")
    if not confirm:
        typer.echo("Operation cancelled.")
        return
    
    try:
        Base.metadata.drop_all(bind=engine)
        typer.echo("🗑️  All tables dropped")
        
        Base.metadata.create_all(bind=engine)
        typer.echo("✅ Database tables recreated successfully!")
    except Exception as e:
        typer.echo(f"❌ Error resetting database: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
