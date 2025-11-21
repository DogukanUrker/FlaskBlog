# FlaskBlog

A modern, **security-hardened** blog application built with Flask, featuring a clean UI, powerful admin tools, and comprehensive security protections.

![FlaskBlog Light Theme](/images/Light.png)
[Watch demo on YouTube](https://youtu.be/WyIpAlSp2RM) — [See screenshots (mobile/desktop, dark/light)](https://github.com/DogukanUrker/flaskBlog/tree/main/images)

## 🆕 Recent Security Updates (v3.0.0dev)

**18 Security Vulnerabilities Fixed!** This version includes comprehensive security improvements:

✅ **Critical Fixes:** Hardcoded credentials removed, file upload validation, open redirect protection
✅ **High Priority:** Rate limiting, account lockout, session security, authorization checks
✅ **Production Ready:** All security headers, secure defaults, environment-based configuration

📖 See [SECURITY_FIXES.md](SECURITY_FIXES.md) for detailed changelog.

## ✨ Features

- **User System** - Registration, login, profiles with custom avatars
- **Two-Factor Authentication (2FA)** - TOTP-based 2FA with backup codes for enhanced account security
- **Rich Editor** - [Milkdown](https://milkdown.dev/) editor for creating beautiful posts
- **Admin Panel** - Full control over users, posts, comments, and security audit logs
- **Security Audit Log** - Track admin logins, user authentication, admin actions, and page access
- **Dark/Light Themes** - Automatic theme switching
- **Categories** - Organize posts by topics
- **Search** - Find posts quickly
- **Responsive Design** - Works great on all devices
- **Analytics** – Tracks post views, visitor countries, and operating systems
- **Advanced Logging** - Powered by [Tamga](https://github.com/dogukanurker/tamga) logger

## 🔒 Security Features

FlaskBlog includes comprehensive security protections:

- **Authentication & Authorization**
  - Two-Factor Authentication (2FA) with TOTP
  - Backup codes for 2FA recovery
  - Email-based 2FA reset (admin-initiated, user-confirmed)
  - Rate limiting (5 attempts, 15-minute lockout)
  - Account lockout mechanism
  - Secure session management (HttpOnly, Secure, SameSite cookies)
  - Generic error messages (prevents username enumeration)
  - Optional Google reCAPTCHA v3 integration

- **File Upload Security**
  - File type validation (whitelist: JPG, PNG, WebP)
  - File size limits (default 5MB)
  - Content verification (prevents fake extensions)
  - Filename sanitization

- **Web Security Headers**
  - Content Security Policy (CSP)
  - X-Frame-Options (clickjacking protection)
  - X-Content-Type-Options (MIME sniffing protection)
  - Strict-Transport-Security (HSTS for HTTPS)
  - Referrer-Policy

- **Additional Protections**
  - CSRF protection (Flask-WTF)
  - SQL injection prevention (parameterized queries)
  - Open redirect protection
  - Secure password hashing (SHA-512)
  - Environment-based configuration (no hardcoded secrets)

- **Security Audit Logging**
  - Comprehensive event tracking for security monitoring
  - Admin login attempts (success and failure)
  - User login attempts (success and failure)
  - Admin panel actions (user deletion, role changes)
  - Sensitive page access (admin panel, login, signup)
  - IP address, user agent, and timestamp logging
  - Filterable by event type (admin logins, user logins, admin actions, page access, rate limits)
  - Admin-only access to security logs

See [SECURITY.md](SECURITY.md) for complete security documentation.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [astral/uv](https://docs.astral.sh/uv/)

### Installation

```bash
# Clone the repository
git clone https://github.com/DogukanUrker/flaskBlog.git
cd flaskBlog

# Configure environment (required for security)
cp .env.example .env
# Edit .env and add your SMTP credentials and secret key

# Fix file permissions (recommended)
chmod +x scripts/fix_permissions.sh
./scripts/fix_permissions.sh

# Run the application
cd app
uv run app.py
```

Visit `http://localhost:1283` in your browser.

### 🐳 Docker Installation (Recommended)

Docker provides an isolated, consistent environment for running FlaskBlog.

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+

**Quick Start with Docker:**

```bash
# Clone the repository
git clone https://github.com/DogukanUrker/flaskBlog.git
cd flaskBlog

# Configure environment
cp .env.example .env
# Edit .env and add your SMTP credentials and secret key

# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

**Production Deployment:**

```bash
# Build the image
docker-compose build

# Run in production mode
docker-compose up -d

# Check container status
docker-compose ps

# Stop the container
docker-compose down
```

**Development Mode:**

```bash
# Run with hot-reload enabled
docker-compose -f docker-compose.dev.yml up

# The source code is mounted as a volume for live changes
```

**Useful Docker Commands:**

```bash
# View application logs
docker-compose logs -f flaskblog

# Access container shell
docker exec -it flaskblog /bin/bash

# Restart the container
docker-compose restart

# Remove containers and volumes (⚠️ deletes database)
docker-compose down -v

# Backup database
docker cp flaskblog:/app/db ./db_backup

# Restore database
docker cp ./db_backup/users.db flaskblog:/app/db/
```

**Docker Features:**

✅ **Isolated environment** - No dependency conflicts
✅ **Security** - Runs as non-root user
✅ **Persistent data** - Database and logs stored in volumes
✅ **Health checks** - Automatic container monitoring
✅ **Resource limits** - CPU and memory constraints
✅ **Easy deployment** - Single command to start

Visit `http://localhost:1283` in your browser.

### Default Admin Account
- Username: `admin`
- Password: `admin`

⚠️ **Important:** Change the default admin password immediately after first login!

### Environment Configuration

Create a `.env` file with your configuration:

```env
# Required
SMTP_PASSWORD=your-smtp-password
APP_SECRET_KEY=generate-with-secrets-module

# Optional (with secure defaults)
DEBUG_MODE=False
SESSION_COOKIE_SECURE=True  # Set to True when using HTTPS
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900  # 15 minutes
```

Generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Admin Panel Features

The admin panel (accessible only to admin users) provides comprehensive management tools:

**User Management** (`/admin/users`)
- View all registered users
- Delete user accounts
- Change user roles (admin ↔ user)
- Reset user 2FA via email confirmation
- View user statistics (points, join date, verification status)

**Post Management** (`/admin/posts`)
- View all blog posts
- Delete posts
- View post statistics (views, comments, categories)

**Comment Management** (`/admin/comments`)
- View all comments
- Delete comments
- Track comment authors and timestamps

**Security Audit Log** (`/admin/security-audit`) ✨ *New*
- Monitor all security-related events in real-time
- Filter by event type:
  - **Admin Logins** - Track admin authentication attempts
  - **User Logins** - Monitor user login activity
  - **Admin Actions** - Review user/post/comment modifications
  - **Page Access** - View sensitive page visits
  - **Rate Limits** - Track rate limiting events
- View detailed information for each event:
  - Username, IP address, user agent
  - Request path, HTTP method, status code
  - Timestamp (date and time)
- Pagination support for large log files

**About Page Settings** (`/admin/about`) ✨ *New*
- Customize the about page content
- Set custom title and markdown content
- Toggle version and GitHub link visibility
- Customize GitHub repository URL
- Customize author website URL
- Set custom credits text

To access the admin panel, login with admin credentials and navigate to `/admin`.

## 🛠️ Tech Stack

**Backend:** Flask, SQLite3, WTForms, Passlib
**Frontend:** TailwindCSS, jQuery, Milkdown Editor
**Icons:** Tabler Icons
**Security:** Flask-WTF (CSRF), reCAPTCHA v3 (optional), Passlib (SHA-512)

## 🧪 Testing

### Security Testing

Test the security features:

```bash
# Test rate limiting (should block after 5 attempts)
for i in {1..6}; do
  curl -X POST http://localhost:1283/login/redirect=/ \
    -d "userName=test&password=wrong"
done

# Test file upload validation (should reject non-image files)
curl -X POST http://localhost:1283/createpost \
  -F "postBanner=@test.txt" \
  -F "postTitle=Test" \
  # ... other required fields
```

### Manual Testing Checklist

- [ ] Login rate limiting works (5 failed attempts → lockout)
- [ ] File uploads reject invalid types (.php, .exe, etc.)
- [ ] File uploads reject oversized files (>5MB)
- [ ] Open redirects are blocked
- [ ] CSRF tokens are validated
- [ ] Session expires after 1 hour
- [ ] Admin panel requires admin role
- [ ] Users can only delete their own posts/comments
- [ ] Security audit log records admin login events
- [ ] Security audit log records admin actions (delete user, change role)
- [ ] Security audit log is accessible only to admins
- [ ] 2FA setup works with authenticator apps
- [ ] 2FA login flow requires TOTP verification
- [ ] 2FA backup codes work for recovery
- [ ] Admin 2FA reset sends email to user for confirmation

## 🔧 Troubleshooting

### Common Issues

**"SMTP credentials not configured"**
```bash
# Add to .env file
SMTP_PASSWORD=your-password
SMTP_MAIL=your-email@example.com
```

**"Permission denied on database files"**
```bash
# Fix with the permissions script
./scripts/fix_permissions.sh
```

**"Rate limit triggered"**
- Wait 15 minutes for lockout to expire
- Or clear failed attempts from database:
```sql
DELETE FROM login_attempts WHERE identifier LIKE '%username%';
```

**"Session expires too quickly"**
```env
# Adjust in .env (in seconds)
PERMANENT_SESSION_LIFETIME=7200  # 2 hours
```

### Debug Mode

Only enable for development:
```env
DEBUG_MODE=True  # NEVER use in production!
```

## 📚 Documentation

- **[SECURITY.md](SECURITY.md)** - Comprehensive security documentation (430+ lines)
- **[SECURITY_FIXES.md](SECURITY_FIXES.md)** - Quick security reference guide
- **[.env.example](.env.example)** - Environment configuration template

### Security Compliance

This application addresses:
- ✅ **OWASP Top 10** - Common web vulnerabilities
- ✅ **CWE-79** - Cross-site Scripting (XSS)
- ✅ **CWE-89** - SQL Injection
- ✅ **CWE-352** - Cross-Site Request Forgery (CSRF)
- ✅ **CWE-601** - Open Redirect
- ✅ **CWE-434** - Unrestricted File Upload
- ✅ **CWE-798** - Hardcoded Credentials

## 🚢 Production Deployment

### Recommended: Docker Deployment

**Docker is the recommended deployment method** for production environments:

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with production values

# 2. Build and deploy
docker-compose build
docker-compose up -d

# 3. Verify deployment
docker-compose ps
docker-compose logs -f
```

**Production Checklist:**

1. ✅ Set `DEBUG_MODE=False` in `.env`
2. ✅ Generate and set a strong `APP_SECRET_KEY`
3. ✅ Configure SMTP credentials for email functionality
4. ✅ Set `SESSION_COOKIE_SECURE=True` (requires HTTPS)
5. ✅ Configure HTTPS/TLS with a reverse proxy (nginx/traefik)
6. ✅ Enable reCAPTCHA (recommended for additional protection)
7. ✅ Set up regular database backups (see Docker backup commands above)
8. ✅ Configure log rotation
9. ✅ Change default admin password
10. ✅ Set resource limits in docker-compose.yml

**Reverse Proxy Setup (nginx example):**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:1283;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Alternative: Manual Deployment

If not using Docker:

```bash
# Install dependencies
cd app
uv sync

# Run with production server (gunicorn)
uv pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:1283 app:app
```

See [SECURITY.md](SECURITY.md) for the complete deployment checklist.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up development environment
cp .env.example .env
DEBUG_MODE=True  # For development only
```

### Code Quality

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Use parameterized queries for database operations
- Validate all user inputs
- Add security checks for sensitive operations

### Security Vulnerabilities

If you discover a security vulnerability, please **do not** open a public issue. Instead, email the maintainer directly with details.

**Responsible Disclosure:**
1. Email security details privately
2. Allow 90 days for patch development
3. Coordinate public disclosure timing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Security audit and fixes by Claude (Anthropic)
- Original project by Doğukan Ürker
- Community contributors

## 👨‍💻 Author

**Doğukan Ürker**
[Website](https://dogukanurker.com) | [Email](mailto:dogukanurker@icloud.com)

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/DogukanUrker/flaskBlog/issues)
- **Discussions:** [GitHub Discussions](https://github.com/DogukanUrker/flaskBlog/discussions)
- **Security:** Email privately (see Contributing section)

---

⭐ **If you find this project useful, please consider giving it a star!**

💡 **Using in production?** Make sure to follow the [Production Deployment](#-production-deployment) checklist!
