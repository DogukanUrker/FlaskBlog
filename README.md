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
- **Rich Editor** - [Milkdown](https://milkdown.dev/) editor for creating beautiful posts
- **Admin Panel** - Full control over users, posts, and comments
- **Dark/Light Themes** - Automatic theme switching
- **Categories** - Organize posts by topics
- **Search** - Find posts quickly
- **Responsive Design** - Works great on all devices
- **Analytics** – Tracks post views, visitor countries, and operating systems
- **Advanced Logging** - Powered by [Tamga](https://github.com/dogukanurker/tamga) logger

## 🔒 Security Features

FlaskBlog includes comprehensive security protections:

- **Authentication & Authorization**
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

Before deploying to production:

1. ✅ Set `DEBUG_MODE=False` in `.env`
2. ✅ Generate and set a strong `APP_SECRET_KEY`
3. ✅ Configure SMTP credentials for email functionality
4. ✅ Set `SESSION_COOKIE_SECURE=True` (requires HTTPS)
5. ✅ Run `./scripts/fix_permissions.sh` to secure file permissions
6. ✅ Configure HTTPS/TLS on your web server
7. ✅ Enable reCAPTCHA (recommended for additional protection)
8. ✅ Set up regular database backups
9. ✅ Configure log rotation
10. ✅ Change default admin password

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
