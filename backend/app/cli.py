import typer
from app.core.database import SessionLocal
from app.models.user import User
from app.services.jsonplaceholder_service import jsonplaceholder_service
from app.services.post_service import post_service
from app.core.security import get_password_hash

app = typer.Typer()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@app.command()
def import_posts(admin_username: str = "admin"):
    """Import posts from JSONPlaceholder"""
    db = get_db()
    
    # Get admin user
    admin_user = db.query(User).filter(User.username == admin_username).first()
    if not admin_user:
        typer.echo(f"Admin user '{admin_username}' not found!")
        typer.echo("Please create an admin user first.")
        return
    
    try:
        typer.echo("Fetching posts from JSONPlaceholder...")
        external_posts = jsonplaceholder_service.get_posts()
        
        typer.echo(f"Found {len(external_posts)} posts to import")
        imported_count = 0
        
        progress_bar = typer.progressbar(
            external_posts, label="Importing posts"
        )
        with progress_bar as progress:
            for ext_post in progress:
                post_service.create_imported_post(
                    db=db,
                    title=ext_post["title"],
                    content=ext_post["body"],
                    author_id=admin_user.id,
                    external_id=ext_post["id"]
                )
                imported_count += 1
        
        typer.echo(f"Successfully imported {imported_count} posts!")
        
    except Exception as e:
        typer.echo(f"Error importing posts: {str(e)}", err=True)
    finally:
        db.close()


@app.command()
def create_admin(
    username: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    full_name: str = typer.Option("", prompt="Full name (optional)")
):
    """Create an admin user"""
    db = get_db()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            typer.echo(
                "User with this username or email already exists!",
                err=True
            )
            return
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            full_name=full_name or None,
            hashed_password=hashed_password,
            is_superuser=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        typer.echo(f"Admin user '{username}' created successfully!")
        
    except Exception as e:
        typer.echo(f"Error creating admin user: {str(e)}", err=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    app()
