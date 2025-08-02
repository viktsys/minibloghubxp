# Production Deployment Guide

This guide covers deploying Mini Blog Hub XP to production with PostgreSQL.

## Prerequisites

- PostgreSQL 12+ installed and running
- Python 3.11+ installed
- Virtual environment set up
- SSL certificate (recommended for HTTPS)

## 1. Environment Setup

### Create Production Environment File

```bash
cp .env.example .env.production
```

Edit `.env.production`:

```env
# Production Settings
DEBUG=false
SECRET_KEY=your-very-secure-secret-key-at-least-32-characters-long

# PostgreSQL Database
POSTGRES_USER=minibloghub_user
POSTGRES_PASSWORD=your-very-secure-database-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=minibloghub_prod

# Or use DATABASE_URL directly
# DATABASE_URL=postgresql://minibloghub_user:password@localhost:5432/minibloghub_prod

# External APIs
UNSPLASH_ACCESS_KEY=your-unsplash-access-key

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
```

## 2. PostgreSQL Setup

### Install PostgreSQL (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Install PostgreSQL (CentOS/RHEL)

```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### Create Database and User

```bash
sudo -u postgres psql
```

```sql
-- Create user
CREATE USER minibloghub_user WITH PASSWORD 'your-very-secure-database-password';

-- Create database
CREATE DATABASE minibloghub_prod OWNER minibloghub_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE minibloghub_prod TO minibloghub_user;

-- Exit psql
\q
```

## 3. Application Deployment

### Install Dependencies

```bash
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

### Database Migration

```bash
# Test database connection
python scripts/db_setup.py check-connection

# Create database tables
python scripts/db_setup.py create-db

# Or use Alembic (preferred for production)
alembic upgrade head

# Create admin user
python scripts/create_admin.py
```

### Test the Application

```bash
# Load production environment
export $(cat .env.production | xargs)

# Test run
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 4. Production Server Setup

### Using Gunicorn

Create a Gunicorn configuration file `gunicorn.conf.py`:

```python
# Gunicorn configuration for production

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 4  # (2 x CPU cores) + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/minibloghub/access.log"
errorlog = "/var/log/minibloghub/error.log"
loglevel = "info"

# Process naming
proc_name = "minibloghub-api"

# Server mechanics
daemon = False
pidfile = "/var/run/minibloghub/minibloghub.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if not using reverse proxy)
# keyfile = "/path/to/private.key"
# certfile = "/path/to/certificate.crt"
```

### Create Systemd Service

Create `/etc/systemd/system/minibloghub.service`:

```ini
[Unit]
Description=Mini Blog Hub XP FastAPI App
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/minibloghub/backend
Environment=PATH=/opt/minibloghub/venv/bin
EnvironmentFile=/opt/minibloghub/backend/.env.production
ExecStart=/opt/minibloghub/venv/bin/gunicorn -c gunicorn.conf.py app.main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable minibloghub

# Start service
sudo systemctl start minibloghub

# Check status
sudo systemctl status minibloghub

# View logs
sudo journalctl -u minibloghub -f
```

## 5. Nginx Reverse Proxy

Install and configure Nginx:

```bash
sudo apt install nginx
```

Create `/etc/nginx/sites-available/minibloghub`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;

    # Logging
    access_log /var/log/nginx/minibloghub.access.log;
    error_log /var/log/nginx/minibloghub.error.log;

    # API routes
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static/ {
        alias /opt/minibloghub/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/minibloghub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 6. SSL Certificate with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 7. Monitoring and Maintenance

### Log Rotation

Create `/etc/logrotate.d/minibloghub`:

```
/var/log/minibloghub/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload minibloghub
    endscript
}
```

### Database Backup

Create a backup script `/opt/minibloghub/scripts/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/minibloghub/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="minibloghub_prod"
DB_USER="minibloghub_user"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /opt/minibloghub/scripts/backup_db.sh
```

## 8. Performance Optimization

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_post_created_at ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_post_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_comment_post_id ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comment_user_id ON comments(user_id);
```

### Connection Pooling

Update your production configuration:

```python
# In app/core/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
)
```

## Troubleshooting

### Check Application Status

```bash
# Check service status
sudo systemctl status minibloghub

# Check logs
sudo journalctl -u minibloghub -f

# Check Nginx logs
sudo tail -f /var/log/nginx/minibloghub.error.log

# Check database connection
python scripts/db_setup.py check-connection
```

### Common Issues

1. **Database connection errors**: Verify PostgreSQL is running and credentials are correct
2. **Permission errors**: Ensure www-data user has proper permissions
3. **SSL certificate issues**: Check certificate paths and renewal
4. **High memory usage**: Monitor and adjust Gunicorn worker count
5. **Slow queries**: Review database indexes and query optimization

For additional support, check the application logs and database performance metrics.
