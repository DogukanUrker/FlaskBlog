# FlaskBlog Migration Guide

This document provides step-by-step instructions for migrating, deploying, or upgrading the FlaskBlog application.

**Version:** 3.0.0dev
**Last Updated:** 2025-11-18

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Fresh Installation](#fresh-installation)
3. [Migration from Older Version](#migration-from-older-version)
4. [Docker Deployment](#docker-deployment)
5. [Manual Deployment](#manual-deployment)
6. [Database Migration](#database-migration)
7. [Data Backup & Restore](#data-backup--restore)
8. [Environment Configuration](#environment-configuration)
9. [Post-Migration Verification](#post-migration-verification)
10. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### System Requirements
- **Python:** 3.9 or higher
- **OS:** Linux, macOS, or Windows
- **RAM:** Minimum 512MB (1GB+ recommended)
- **Disk Space:** Minimum 500MB
- **Network:** Required for CDN resources (or use local vendor files)

### Required Dependencies
```bash
# Core dependencies
flask>=3.1.0
flask-wtf>=1.2.2
wtforms>=3.2.1
passlib>=1.7.4

# Database & Storage
sqlite3 (built-in with Python)

# Security & Utilities
geoip2>=5.0.1
user-agents>=2.2.0
tamga>=1.4.0
markdown2
bleach
html2text

# 2FA Support
pyotp>=2.9.0
qrcode>=7.4.2
pillow>=10.0.0
```

---

## Fresh Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/DogukanUrker/flaskBlog.git
cd flaskBlog
```

### Step 2: Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or your preferred editor
```

**Required environment variables:**
```env
# Application
APP_SECRET_KEY=your-secret-key-here-use-secrets-token-hex-32
APP_HOST=0.0.0.0
APP_PORT=1283
DEBUG_MODE=False

# SMTP Configuration (for password reset)
SMTP_PASSWORD=your-smtp-password
SMTP_MAIL=your-email@example.com

# Session Security
SESSION_COOKIE_SECURE=True  # Requires HTTPS
PERMANENT_SESSION_LIFETIME=3600

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900

# File Uploads
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes
ALLOWED_UPLOAD_EXTENSIONS=jpg,jpeg,png,webp
```

### Step 3: Install Dependencies
```bash
cd app

# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# OR using pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Database Initialization
```bash
# The application auto-creates databases on first run
python3 app.py

# Databases will be created in app/db/:
# - users.db
# - posts.db
# - comments.db
# - analytics.db
```

### Step 5: Set Permissions (Linux/macOS)
```bash
chmod +x ../scripts/fix_permissions.sh
../scripts/fix_permissions.sh
```

### Step 6: Access Application
```
http://localhost:1283
```

**Default admin credentials:**
- Username: `admin`
- Password: `admin`

**⚠️ IMPORTANT:** Change default admin password immediately after first login!

---

## Migration from Older Version

### Version 2.x → 3.0.0dev

#### Breaking Changes
1. **2FA Support Added**: New database columns in Users table
2. **File Upload Validation**: New error code system
3. **Default Banner System**: New utility module
4. **Session Security**: Enhanced session management
5. **Host Binding**: Default changed from localhost to 0.0.0.0

#### Migration Steps

**Step 1: Backup Existing Data**
```bash
# Backup all databases
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp app/db/*.db backups/$(date +%Y%m%d_%H%M%S)/

# Backup environment file
cp .env backups/$(date +%Y%m%d_%H%M%S)/.env.backup
```

**Step 2: Pull Latest Changes**
```bash
git fetch origin
git checkout main  # or your target branch
git pull origin main
```

**Step 3: Update Dependencies**
```bash
cd app
source .venv/bin/activate

# Update all dependencies
uv pip install --upgrade -r requirements.txt

# OR with pip
pip install --upgrade -r requirements.txt
```

**Step 4: Database Schema Update**
The application uses automatic schema migration via `dbChecker.py`. Run the app to apply changes:

```bash
python3 app.py
```

The following tables will be automatically updated:
- **Users**: Add `twofa_secret`, `twofa_enabled`, `backup_codes` columns
- **login_attempts**: No changes (already exists)
- **password_reset_tokens**: No changes (already exists)

**Step 5: Update Environment Variables**
Add new variables to `.env`:
```env
# New in 3.0.0dev
APP_HOST=0.0.0.0  # Changed from localhost
MAX_UPLOAD_SIZE=5242880
ALLOWED_UPLOAD_EXTENSIONS=jpg,jpeg,png,webp
```

**Step 6: Verify Migration**
```bash
# Check logs for successful migration
tail -f logs/app.log

# Look for:
# - "Column: twofa_secret added to Users table"
# - "Column: twofa_enabled added to Users table"
# - "Column: backup_codes added to Users table"
```

**Step 7: Test Critical Features**
- [ ] Login with existing credentials
- [ ] Create new post
- [ ] Upload post banner
- [ ] Enable 2FA on test account
- [ ] Password reset flow
- [ ] Admin panel access

---

## Docker Deployment

### Build Docker Image
```bash
# From project root
docker build -t flaskblog:3.0.0dev .
```

### Run with Docker
```bash
docker run -d \
  --name flaskblog \
  -p 1283:1283 \
  -v $(pwd)/app/db:/app/db \
  -v $(pwd)/app/log:/app/log \
  -e APP_SECRET_KEY=your-secret-key \
  -e SMTP_PASSWORD=your-smtp-password \
  -e SMTP_MAIL=your-email@example.com \
  flaskblog:3.0.0dev
```

### Docker Compose (Recommended)
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  flaskblog:
    build: .
    container_name: flaskblog
    ports:
      - "1283:1283"
    volumes:
      - ./app/db:/app/db
      - ./app/log:/app/log
    environment:
      - APP_SECRET_KEY=${APP_SECRET_KEY}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMTP_MAIL=${SMTP_MAIL}
      - DEBUG_MODE=False
      - SESSION_COOKIE_SECURE=True
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python3", "-c", "import socket; sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.settimeout(2); result = sock.connect_ex(('localhost', 1283)); sock.close(); exit(result)"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Deploy:**
```bash
docker-compose up -d
```

---

## Manual Deployment

### Nginx Reverse Proxy
Create `/etc/nginx/sites-available/flaskblog`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://127.0.0.1:1283;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (optional optimization)
    location /static/ {
        alias /path/to/flaskBlog/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/flaskblog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Systemd Service
Create `/etc/systemd/system/flaskblog.service`:
```ini
[Unit]
Description=FlaskBlog Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/flaskBlog/app
Environment="PATH=/path/to/flaskBlog/app/.venv/bin"
ExecStart=/path/to/flaskBlog/app/.venv/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable flaskblog
sudo systemctl start flaskblog
sudo systemctl status flaskblog
```

---

## Database Migration

### Schema Changes in 3.0.0dev

#### Users Table
```sql
-- New columns for 2FA support
ALTER TABLE Users ADD COLUMN twofa_secret TEXT DEFAULT NULL;
ALTER TABLE Users ADD COLUMN twofa_enabled TEXT DEFAULT "False";
ALTER TABLE Users ADD COLUMN backup_codes TEXT DEFAULT NULL;
```

These migrations are **automatic** via `dbChecker.py`. Manual intervention is only needed if:
- You have custom database modifications
- Migration fails during startup
- You need to rollback changes

### Manual Migration (if needed)
```bash
# Connect to database
sqlite3 app/db/users.db

# Check current schema
.schema Users

# Manually add columns if auto-migration failed
ALTER TABLE Users ADD COLUMN twofa_secret TEXT DEFAULT NULL;
ALTER TABLE Users ADD COLUMN twofa_enabled TEXT DEFAULT "False";
ALTER TABLE Users ADD COLUMN backup_codes TEXT DEFAULT NULL;

# Verify changes
.schema Users
.quit
```

---

## Data Backup & Restore

### Backup All Data
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup databases
cp app/db/*.db "$BACKUP_DIR/"

# Backup environment
cp .env "$BACKUP_DIR/.env.backup"

# Backup logs (optional)
cp -r app/log "$BACKUP_DIR/log_backup"

echo "Backup created: $BACKUP_DIR"
```

### Restore from Backup
```bash
#!/bin/bash
# restore.sh

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: ./restore.sh <backup_directory>"
    exit 1
fi

# Stop application
systemctl stop flaskblog  # or docker-compose down

# Restore databases
cp "$BACKUP_DIR"/*.db app/db/

# Restore environment
cp "$BACKUP_DIR/.env.backup" .env

# Restart application
systemctl start flaskblog  # or docker-compose up -d

echo "Restore completed from: $BACKUP_DIR"
```

### Automated Backups
Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/flaskBlog/scripts/backup.sh
```

---

## Environment Configuration

### Production Checklist
- [ ] Set `DEBUG_MODE=False`
- [ ] Generate strong `APP_SECRET_KEY` (32+ bytes)
- [ ] Configure SMTP credentials
- [ ] Enable `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- [ ] Set appropriate `PERMANENT_SESSION_LIFETIME`
- [ ] Configure `MAX_LOGIN_ATTEMPTS` and `LOCKOUT_DURATION`
- [ ] Set `MAX_UPLOAD_SIZE` and `ALLOWED_UPLOAD_EXTENSIONS`
- [ ] Change default admin password
- [ ] Enable firewall rules
- [ ] Set up SSL/TLS certificates
- [ ] Configure database backups
- [ ] Set up log rotation

### Generate Secret Key
```python
import secrets
print(secrets.token_hex(32))
```

### Environment Variables Reference
| Variable | Default | Description |
|----------|---------|-------------|
| `APP_SECRET_KEY` | **Required** | Flask secret key (64 chars hex) |
| `APP_HOST` | `0.0.0.0` | Host to bind to |
| `APP_PORT` | `1283` | Port to listen on |
| `DEBUG_MODE` | `False` | Enable debug mode (dev only!) |
| `SMTP_PASSWORD` | **Required** | SMTP server password |
| `SMTP_MAIL` | **Required** | SMTP sender email |
| `SESSION_COOKIE_SECURE` | `True` | Require HTTPS for cookies |
| `PERMANENT_SESSION_LIFETIME` | `3600` | Session timeout (seconds) |
| `MAX_LOGIN_ATTEMPTS` | `5` | Failed login threshold |
| `LOCKOUT_DURATION` | `900` | Account lockout time (seconds) |
| `MAX_UPLOAD_SIZE` | `5242880` | Max file upload (bytes) |

---

## Post-Migration Verification

### Automated Tests
```bash
# Run application in test mode
cd app
python3 -m pytest tests/  # if tests exist

# Manual verification
python3 app.py
```

### Manual Verification Checklist
- [ ] Application starts without errors
- [ ] Database files exist in `app/db/`
- [ ] Login with admin credentials works
- [ ] Create new user account
- [ ] Enable 2FA on test account
- [ ] Create new blog post
- [ ] Upload post banner (or verify default banner)
- [ ] Post comment on blog
- [ ] Password reset flow works
- [ ] Admin panel accessible
- [ ] Theme switching works
- [ ] Language switching works
- [ ] Search functionality works
- [ ] Analytics tracking works (if enabled)

### Health Check
```bash
# Check if application is running
curl http://localhost:1283

# Check database connections
sqlite3 app/db/users.db "SELECT COUNT(*) FROM Users;"
sqlite3 app/db/posts.db "SELECT COUNT(*) FROM posts;"
```

---

## Rollback Procedures

### Rollback to Previous Version

**Step 1: Stop Application**
```bash
systemctl stop flaskblog
# OR
docker-compose down
```

**Step 2: Restore Backup**
```bash
# Restore databases
cp backups/YYYYMMDD_HHMMSS/*.db app/db/

# Restore environment
cp backups/YYYYMMDD_HHMMSS/.env.backup .env
```

**Step 3: Checkout Previous Version**
```bash
git log --oneline  # Find previous commit
git checkout <commit-hash>
```

**Step 4: Downgrade Dependencies (if needed)**
```bash
cd app
pip install -r requirements.txt --force-reinstall
```

**Step 5: Restart Application**
```bash
systemctl start flaskblog
# OR
docker-compose up -d
```

### Database Rollback
If database schema changes cause issues:
```bash
# Connect to database
sqlite3 app/db/users.db

# Remove new columns (2FA columns)
ALTER TABLE Users DROP COLUMN twofa_secret;
ALTER TABLE Users DROP COLUMN twofa_enabled;
ALTER TABLE Users DROP COLUMN backup_codes;

.quit
```

**Note:** SQLite doesn't support `DROP COLUMN` in older versions. Alternative:
```sql
-- Create new table without 2FA columns
CREATE TABLE Users_backup AS
SELECT userID, userName, email, password, profilePicture, role, points, timeStamp, isVerified
FROM Users;

-- Drop old table
DROP TABLE Users;

-- Rename backup
ALTER TABLE Users_backup RENAME TO Users;
```

---

## Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'PIL'"**
```bash
pip install pillow
```

**2. "Database is locked"**
```bash
# Check for open connections
lsof | grep users.db

# Kill processes if necessary
pkill -f app.py

# Restart application
```

**3. "Permission denied on database files"**
```bash
chmod +x scripts/fix_permissions.sh
./scripts/fix_permissions.sh
```

**4. "CSRF token missing or invalid"**
- Clear browser cookies
- Check `APP_SECRET_KEY` is set
- Verify session configuration

**5. "Account locked after migration"**
```sql
-- Clear failed login attempts
sqlite3 app/db/users.db
DELETE FROM login_attempts;
.quit
```

---

## Support & Resources

- **Documentation:** [README.md](README.md)
- **Security Guide:** [SECURITY.md](SECURITY.md)
- **AI Assistant Guide:** [CLAUDE.md](CLAUDE.md)
- **GitHub Issues:** https://github.com/DogukanUrker/flaskBlog/issues
- **Author:** Doğukan Ürker - dogukanurker@icloud.com

---

**Last Updated:** 2025-11-18
**Document Version:** 1.0.0
