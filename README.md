# FlaskBlog

A modern blog application built with Flask, featuring a clean UI and powerful admin tools. 

![FlaskBlog Light Theme](/images/Light.png)
[Watch demo on YouTube](https://youtu.be/WyIpAlSp2RM) — [See screenshots (mobile/desktop, dark/light)](https://github.com/DogukanUrker/flaskBlog/tree/main/images)

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

**Backend:** Flask, SQLite3, WTForms, Passlib \
**Frontend:** TailwindCSS, jQuery, Summer Note Editor \
**Icons:** Tabler Icons

## 📚 Documentation

- **[SECURITY.md](SECURITY.md)** - Comprehensive security documentation
- **[SECURITY_FIXES.md](SECURITY_FIXES.md)** - Quick security reference guide
- **[.env.example](.env.example)** - Environment configuration template

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

### Security Vulnerabilities

If you discover a security vulnerability, please **do not** open a public issue. Instead, email the maintainer directly with details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Doğukan Ürker** \
[Website](https://dogukanurker.com) | [Email](mailto:dogukanurker@icloud.com)

---

⭐ If you find this project useful, please consider giving it a star!
