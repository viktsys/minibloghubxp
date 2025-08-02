# Mini Blog Hub XP - Backend

FastAPI backend application for the Mini Blog Hub XP project.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **SQLAlchemy ORM**: Database operations with SQLite (dev) and PostgreSQL (prod)
- **JWT Authentication**: Secure user authentication
- **External API Integration**: JSONPlaceholder and Unsplash APIs
- **Rate Limiting**: API protection with slowapi
- **Auto Documentation**: OpenAPI/Swagger documentation
- **Database Migrations**: Alembic for schema management

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

#### Development (SQLite)
For development, edit `.env` with:

```env
DEBUG=true
SECRET_KEY=your-secret-key-for-jwt-change-this-in-production
DATABASE_URL=sqlite:///./blog.db
UNSPLASH_ACCESS_KEY=your-unsplash-access-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

#### Production (PostgreSQL)
For production with PostgreSQL, edit `.env` with:

```env
DEBUG=false
SECRET_KEY=your-very-secure-secret-key-for-production

# PostgreSQL Configuration
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_secure_postgres_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=minibloghub_prod

# Or use a complete DATABASE_URL
# DATABASE_URL=postgresql://user:password@localhost:5432/minibloghub_prod

UNSPLASH_ACCESS_KEY=your-unsplash-access-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

### 4. Database Setup

#### Option 1: Using the Database Setup Script (Recommended)
```bash
# Check database connection and configuration
python scripts/db_setup.py show-config

# Test database connection
python scripts/db_setup.py check-connection

# Create database tables
python scripts/db_setup.py create-db
```

#### Option 2: Manual Setup
```bash
# Create database tables
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Or use Alembic migrations (when available)
# alembic upgrade head
```

#### PostgreSQL Setup for Production
1. Install PostgreSQL on your system
2. Create a database and user:
```sql
CREATE DATABASE minibloghub_prod;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE minibloghub_prod TO your_user;
```
3. Update your `.env` file with PostgreSQL credentials
4. Run the database setup script

### 5. Create Admin User

```bash
python scripts/create_admin.py
```

Or using the CLI:

```bash
python -m app.cli create-admin
```

### 6. Import Sample Posts (Optional)

```bash
python -m app.cli import-posts
```

## Running the Application

### Development (SQLite)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (PostgreSQL)

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker Compose (Recommended for Development/Testing)

The project includes a `docker-compose.yml` file that sets up both the application and PostgreSQL database:

```bash
# Start the application with PostgreSQL
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Stop and remove volumes (removes database data)
docker-compose down -v
```

This will start:
- **FastAPI application** on `http://localhost:8000`
- **PostgreSQL database** on `localhost:5432`
- **pgAdmin** (database management) on `http://localhost:5050`
  - Email: `admin@example.com`
  - Password: `admin`

### Building Docker Image

```bash
# Build the Docker image
docker build -t minibloghub-api .

# Run the container
docker run -p 8000:8000 minibloghub-api
```

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Posts
- `GET /api/v1/posts/` - List posts (with pagination)
- `POST /api/v1/posts/` - Create new post
- `GET /api/v1/posts/{id}` - Get specific post
- `PUT /api/v1/posts/{id}` - Update post
- `DELETE /api/v1/posts/{id}` - Delete post
- `POST /api/v1/posts/import/` - Import posts from JSONPlaceholder

### Comments
- `GET /api/v1/posts/{id}/comments/` - List comments for post
- `POST /api/v1/posts/{id}/comments/` - Create comment
- `PUT /api/v1/posts/comments/{id}` - Update comment
- `DELETE /api/v1/posts/comments/{id}` - Delete comment

### Images
- `GET /api/v1/images/search/` - Search images on Unsplash
- `GET /api/v1/images/{id}` - Get image details
- `POST /api/v1/images/select/` - Select image (trigger download)

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── posts.py        # Posts endpoints
│   │   │   ├── comments.py     # Comments endpoints
│   │   │   └── images.py       # Image search endpoints
│   │   └── deps.py             # API dependencies
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database connection
│   │   └── security.py         # Security utilities
│   ├── models/
│   │   ├── user.py             # User model
│   │   ├── post.py             # Post model
│   │   └── comment.py          # Comment model
│   ├── schemas/
│   │   ├── user.py             # User Pydantic schemas
│   │   ├── post.py             # Post Pydantic schemas
│   │   └── comment.py          # Comment Pydantic schemas
│   ├── services/
│   │   ├── jsonplaceholder_service.py  # JSONPlaceholder API
│   │   ├── unsplash_service.py         # Unsplash API
│   │   └── post_service.py             # Post business logic
│   ├── cli.py                  # Command line interface
│   └── main.py                 # FastAPI application
├── alembic/                    # Database migrations
├── scripts/
│   └── create_admin.py         # Admin user creation script
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Alembic configuration
└── .env.example               # Environment variables example
```

## CLI Commands

The application includes a CLI for common tasks:

```bash
# Create admin user
python -m app.cli create-admin

# Import posts from JSONPlaceholder
python -m app.cli import-posts --admin-username admin
```

## Development

### Code Style

The project follows PEP 8 style guidelines. You can check code style with:

```bash
flake8 app/
```

### Testing

Run tests with:

```bash
pytest
```

## External APIs

### JSONPlaceholder

Used for importing sample posts. No API key required.

- **Base URL**: https://jsonplaceholder.typicode.com/
- **Endpoints Used**:
  - `/posts` - Get all posts
  - `/posts/{id}` - Get specific post
  - `/posts/{id}/comments` - Get post comments

### Unsplash

Used for searching and selecting images for posts.

- **Base URL**: https://api.unsplash.com/
- **Authentication**: Client-ID header
- **Endpoints Used**:
  - `/search/photos` - Search photos
  - `/photos/{id}` - Get photo details

To use Unsplash:
1. Create account at https://unsplash.com/developers
2. Create a new application
3. Copy the Access Key to your `.env` file

## Docker Support (Optional)

Create a `Dockerfile` for containerization:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | JWT secret key | Required |
| `DATABASE_URL` | Database connection URL | `sqlite:///./blog.db` |
| `UNSPLASH_ACCESS_KEY` | Unsplash API access key | Optional |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` |
| `ALGORITHM` | JWT algorithm | `HS256` |

## License

This project is part of the Mini Blog Hub XP technical test.
