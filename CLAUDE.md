# FlaskBlog - AI Assistant Guide

This document provides comprehensive guidance for AI assistants working with the FlaskBlog codebase. It covers architecture, conventions, workflows, and best practices.

**Version:** 3.0.0dev
**Last Updated:** 2025-11-18
**Python Version:** 3.9+

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Codebase Structure](#codebase-structure)
3. [Technology Stack](#technology-stack)
4. [Architecture & Patterns](#architecture--patterns)
5. [Database Schema](#database-schema)
6. [Development Workflows](#development-workflows)
7. [Code Conventions](#code-conventions)
8. [Security Guidelines](#security-guidelines)
9. [Common Tasks](#common-tasks)
10. [Testing Strategy](#testing-strategy)
11. [Debugging & Troubleshooting](#debugging--troubleshooting)
12. [Deployment Considerations](#deployment-considerations)

---

## Repository Overview

FlaskBlog is a **security-hardened** blog application built with Flask, featuring user authentication, markdown-based post creation, admin panel, analytics tracking, and internationalization support for 12 languages.

### Key Features
- User authentication with rate limiting and account lockout
- Markdown-based post editor (Milkdown)
- Admin panel for user/post/comment management
- Analytics tracking (views, geolocation, OS detection)
- 12 language support
- 35 DaisyUI themes
- Security headers, CSRF protection, file upload validation
- Password reset with secure token management

### Project Statistics
- **150+ Python files**
- **34 HTML templates**
- **27 route blueprints**
- **6 database tables**
- **12 supported languages**
- **50+ endpoints**

---

## Codebase Structure

```
FlaskBlog/
├── app/
│   ├── app.py                    # Main application entry point
│   ├── settings.py               # Configuration management
│   ├── pyproject.toml            # Dependencies & metadata
│   │
│   ├── routes/                   # Blueprint route handlers (27 files)
│   │   ├── about.py
│   │   ├── accountSettings.py
│   │   ├── adminPanel*.py        # Admin panel modules
│   │   ├── category.py
│   │   ├── createPost.py
│   │   ├── editPost.py
│   │   ├── index.py              # Homepage
│   │   ├── login.py
│   │   ├── post.py               # Single post view
│   │   ├── search.py
│   │   └── ...
│   │
│   ├── templates/                # Jinja2 templates (34 files)
│   │   ├── layout.html           # Master template
│   │   ├── components/           # Reusable components
│   │   │   ├── navbar.html
│   │   │   ├── pagination.html
│   │   │   ├── postCardMacro.html
│   │   │   └── ...
│   │   └── *.html                # Page templates
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── general.css       # Global styles
│   │   │   ├── markdown.css      # Markdown rendering
│   │   │   └── ...
│   │   └── js/
│   │       ├── markdownEditor.js # Milkdown integration
│   │       ├── navbar.js
│   │       └── ...
│   │
│   ├── utils/                    # Utility modules
│   │   ├── dbChecker.py          # Database schema initialization
│   │   ├── rateLimiter.py        # Rate limiting & lockout
│   │   ├── fileUploadValidator.py # File upload security
│   │   ├── redirectValidator.py  # Open redirect protection
│   │   ├── secureTokenManager.py # Password reset tokens
│   │   ├── markdown_renderer.py  # Markdown to HTML
│   │   ├── delete.py             # Delete operations
│   │   ├── paginate.py           # Pagination helper
│   │   │
│   │   ├── forms/                # WTForms validation
│   │   │   ├── LoginForm.py
│   │   │   ├── SignUpForm.py
│   │   │   └── ...
│   │   │
│   │   ├── contextProcessor/     # Template context injectors
│   │   │   ├── injectTranslations.py
│   │   │   ├── isLogin.py
│   │   │   └── ...
│   │   │
│   │   ├── errorHandlers/        # HTTP error handlers
│   │   │   ├── notFoundErrorHandler.py
│   │   │   ├── unauthorizedErrorHandler.py
│   │   │   └── csrfErrorHandler.py
│   │   │
│   │   └── beforeRequest/        # Pre-request hooks
│   │       └── browserLanguage.py
│   │
│   ├── translations/             # i18n JSON files
│   │   ├── en.json
│   │   ├── tr.json
│   │   └── ... (12 languages total)
│   │
│   └── db/                       # SQLite databases (gitignored)
│       ├── users.db
│       ├── posts.db
│       ├── comments.db
│       └── analytics.db
│
├── scripts/
│   └── fix_permissions.sh        # Database file permissions
│
├── docs/                         # Documentation
├── .env.example                  # Environment template
├── .gitignore
├── README.md
├── SECURITY.md
└── SECURITY_FIXES.md
```

---

## Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Flask** | 3.1.0+ | Web framework |
| **SQLite3** | - | Database (4 separate DB files) |
| **Flask-WTF** | 1.2.2+ | CSRF protection & forms |
| **WTForms** | 3.2.1+ | Form validation |
| **Passlib** | 1.7.4+ | Password hashing (SHA-512) |
| **GeoIP2** | 5.0.1+ | IP geolocation for analytics |
| **user-agents** | 2.2.0+ | User agent parsing |
| **Tamga** | 1.4.0+ | Advanced logging |
| **markdown2** | - | Markdown rendering |
| **bleach** | - | HTML sanitization |

### Frontend
| Technology | Source | Purpose |
|------------|--------|---------|
| **Tailwind CSS** | CDN | Utility-first CSS framework |
| **DaisyUI v5** | CDN | Component library (35 themes) |
| **Milkdown** | - | WYSIWYG markdown editor |
| **jQuery 3.4.1** | - | DOM manipulation |
| **Tabler Icons** | CDN | SVG icon library |

### Security
- **CSRFProtect** (Flask-WTF) - CSRF token validation
- **Bleach** - HTML sanitization in markdown
- **Custom RateLimiter** - Brute force protection
- **FileUploadValidator** - File upload security
- **RedirectValidator** - Open redirect prevention
- **SecureTokenManager** - Password reset tokens

---

## Architecture & Patterns

### 1. Blueprint-Based Architecture

Each feature area is isolated as a Flask Blueprint:

```python
# routes/createPost.py
from flask import Blueprint

createPostBlueprint = Blueprint("createPost", __name__)

@createPostBlueprint.route("/createpost", methods=["GET", "POST"])
def createPost():
    # Route logic
    pass
```

**Registration in app.py:**
```python
app.register_blueprint(createPostBlueprint)
```

**Key Benefits:**
- Modular organization
- Easy to add/remove features
- Clear separation of concerns

### 2. Context Processor Pattern

Global template variables injected via context processors:

**Location:** `app/utils/contextProcessor/`

```python
# contextProcessor/isLogin.py
from settings import Settings

def isLogin():
    return {"loginEnabled": Settings.LOG_IN}
```

**Usage in templates:**
```jinja2
{% if loginEnabled %}
  <a href="/login">Login</a>
{% endif %}
```

**Available Context Processors:**
- `isLogin()` - Login feature toggle
- `injectTranslations()` - i18n translations
- `returnUserProfilePicture()` - User avatar for navbar
- `returnPostUrlID()` - Post URL generation helper
- `markdown_processor()` - Markdown rendering function

### 3. Stateless Request Handling

- Session data stored in Flask session (signed cookies)
- Database queries per request (no ORM caching)
- No global state between requests
- Logging of all significant actions

### 4. Database Access Pattern

**No ORM - Direct SQLite3 usage:**

```python
import sqlite3
from settings import Settings

# Parameterized queries to prevent SQL injection
db = sqlite3.connect(Settings.DB_USERS_ROOT)
cursor = db.cursor()
cursor.execute(
    "SELECT * FROM Users WHERE userName = ?",
    (userName,)
)
user = cursor.fetchone()
db.close()
```

**Key Principles:**
- Always use parameterized queries (never f-strings!)
- Close connections after use
- Log database operations
- Handle exceptions gracefully

### 5. Error Handling Strategy

**HTTP Error Handlers:**
- `404` → `templates/notFound.html`
- `401` → `templates/unauthorized.html`
- `CSRF errors` → `templates/csrfError.html`

**Flash Messages for User Feedback:**
```python
from utils.flashMessage import flashMessage

flashMessage("success", translations["successMessageKey"])
flashMessage("error", translations["errorMessageKey"])
```

### 6. Security-First Design

Every user input passes through multiple security layers:

1. **CSRF Protection** - All forms validated with tokens
2. **Input Validation** - WTForms validators
3. **SQL Injection Prevention** - Parameterized queries
4. **XSS Prevention** - Bleach sanitization + template escaping
5. **File Upload Validation** - Content verification, size limits
6. **Rate Limiting** - Failed login attempt tracking
7. **Authorization Checks** - User ownership verification

---

## Database Schema

FlaskBlog uses **4 separate SQLite databases** for performance and organization.

### Users Database (`db/users.db`)

#### `Users` Table
```sql
CREATE TABLE Users(
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    userName TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT,              -- SHA-512 hashed
    profilePicture TEXT,        -- DiceBear API URL
    role TEXT,                  -- "admin" or "user"
    points INTEGER,             -- Gamification points
    timeStamp INTEGER,          -- Creation timestamp
    isVerified TEXT             -- "True" or "False"
);
```

#### `login_attempts` Table (Rate Limiting)
```sql
CREATE TABLE login_attempts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT,            -- IP:hash(UserAgent)
    attempt_time INTEGER,
    success INTEGER DEFAULT 0
);
```

#### `password_reset_tokens` Table
```sql
CREATE TABLE password_reset_tokens(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userName TEXT,
    token TEXT UNIQUE,          -- 32-byte secure token
    created_at INTEGER,
    expires_at INTEGER,         -- 15-minute expiry
    used INTEGER DEFAULT 0
);
```

### Posts Database (`db/posts.db`)

#### `posts` Table
```sql
CREATE TABLE posts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    tags TEXT,
    content TEXT,               -- Markdown content
    banner BLOB,                -- Post banner image
    author TEXT,
    views INTEGER,
    timeStamp INTEGER,
    lastEditTimeStamp INTEGER,
    category TEXT,
    urlID TEXT,                 -- URL-friendly identifier
    abstract TEXT               -- Post summary (150-200 chars)
);
```

### Comments Database (`db/comments.db`)

#### `comments` Table
```sql
CREATE TABLE comments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post INTEGER,               -- Foreign key to posts.id
    comment TEXT,
    user TEXT,                  -- Username
    timeStamp INTEGER
);
```

### Analytics Database (`db/analytics.db`)

#### `postsAnalytics` Table
```sql
CREATE TABLE postsAnalytics(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    postID INTEGER,
    visitorUserName TEXT,
    country TEXT,               -- From GeoIP2
    os TEXT,                    -- From user-agent
    continent TEXT,
    timeSpendDuration INT,
    timeStamp INTEGER
);
```

---

## Development Workflows

### Initial Setup

```bash
# Clone repository
git clone https://github.com/DogukanUrker/flaskBlog.git
cd flaskBlog

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Fix permissions
chmod +x scripts/fix_permissions.sh
./scripts/fix_permissions.sh

# Run application
cd app
uv run app.py
```

### Environment Configuration

**Required variables in `.env`:**
```env
APP_SECRET_KEY=generate-with-secrets-module
SMTP_PASSWORD=your-smtp-password
```

**Optional variables:**
```env
DEBUG_MODE=False
SESSION_COOKIE_SECURE=True
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900
MAX_UPLOAD_SIZE=5242880
```

### Adding a New Route

1. **Create blueprint file:**
```python
# app/routes/newFeature.py
from flask import Blueprint, render_template

newFeatureBlueprint = Blueprint("newFeature", __name__)

@newFeatureBlueprint.route("/new-feature", methods=["GET"])
def newFeature():
    return render_template("newFeature.html")
```

2. **Register blueprint in app.py:**
```python
from routes.newFeature import newFeatureBlueprint

app.register_blueprint(newFeatureBlueprint)
```

3. **Create template:**
```jinja2
<!-- templates/newFeature.html -->
{% extends "layout.html" %}
{% block title %}New Feature{% endblock %}
{% block content %}
  <!-- Content here -->
{% endblock %}
```

### Adding a New Form

1. **Create form class:**
```python
# app/utils/forms/NewForm.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class NewForm(FlaskForm):
    fieldName = StringField(
        "Label",
        validators=[DataRequired(), Length(min=3, max=50)],
        render_kw={"placeholder": "Enter text"}
    )
    submit = SubmitField("Submit")
```

2. **Use in route:**
```python
from utils.forms.NewForm import NewForm

@blueprint.route("/route", methods=["GET", "POST"])
def route():
    form = NewForm()
    if form.validate_on_submit():
        # Process form data
        pass
    return render_template("template.html", form=form)
```

3. **Render in template:**
```jinja2
<form method="POST">
    {{ form.csrf_token }}
    {{ form.fieldName(class="input") }}
    {{ form.submit(class="btn btn-primary") }}
</form>
```

### Database Migrations

**No automated migrations - manual schema changes:**

1. **Backup existing databases:**
```bash
cp app/db/users.db app/db/users.db.backup
```

2. **Update schema in dbChecker.py:**
```python
# utils/dbChecker.py
cursor.execute("""
    ALTER TABLE tableName
    ADD COLUMN newColumn TEXT;
""")
```

3. **Run application to apply changes:**
```bash
cd app && uv run app.py
```

### Adding Translations

1. **Add keys to all language files:**
```json
// translations/en.json
{
  "newKey": "English text"
}

// translations/tr.json
{
  "newKey": "Türkçe metin"
}
```

2. **Use in templates:**
```jinja2
{{ translations.newKey }}
```

3. **Use in Python:**
```python
from utils.translations import Translations

translations = Translations.getTranslations(session.get("language", "en"))
flashMessage("info", translations["newKey"])
```

---

## Code Conventions

### Python Style

**Follow PEP 8 with these specifics:**

- **Imports:** Group stdlib, third-party, local
```python
import os
from datetime import timedelta

from flask import Flask, render_template
from flask_wtf import FlaskForm

from settings import Settings
from utils.log import Log
```

- **Docstrings:** Use for all functions
```python
def functionName(param1, param2):
    """
    Brief description of function.

    Args:
        param1 (str): Description
        param2 (int): Description

    Returns:
        bool: Description
    """
    pass
```

- **Database operations:** Always use parameterized queries
```python
# GOOD ✅
cursor.execute("SELECT * FROM Users WHERE userName = ?", (userName,))

# BAD ❌ - SQL injection vulnerability!
cursor.execute(f"SELECT * FROM Users WHERE userName = '{userName}'")
```

- **Error handling:** Log errors with Tamga
```python
from utils.log import Log

try:
    # Code
except Exception as e:
    Log().error(f"Error message: {e}")
```

### Template Conventions

- **Extend layout.html:**
```jinja2
{% extends "layout.html" %}
```

- **Define blocks:**
```jinja2
{% block title %}Page Title{% endblock %}
{% block content %}
  <!-- Content -->
{% endblock %}
```

- **Use components:**
```jinja2
{% include 'components/navbar.html' %}
```

- **Flash messages:**
```jinja2
{% include 'components/flash.html' %}
```

- **Escape user content:**
```jinja2
{{ userContent|e }}  {# Auto-escaped by Jinja2 #}
```

### JavaScript Conventions

- **jQuery usage:**
```javascript
$(document).ready(function() {
    // Code here
});
```

- **AJAX requests include CSRF tokens:**
```javascript
$.ajax({
    url: "/endpoint",
    method: "POST",
    headers: {
        "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
    },
    data: { key: value }
});
```

### CSS Conventions

- **Use Tailwind utility classes:**
```html
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-4">Title</h1>
</div>
```

- **Use DaisyUI components:**
```html
<button class="btn btn-primary">Click Me</button>
<div class="alert alert-success">Success message</div>
```

- **Custom CSS in static/css/general.css:**
```css
/* Only for styles not achievable with Tailwind */
.custom-class {
    /* Custom styles */
}
```

---

## Security Guidelines

### Authentication & Authorization

**Always check user authentication:**
```python
if "userName" not in session:
    flashMessage("error", translations["loginRequired"])
    return redirect("/login/redirect=" + request.path)
```

**Check authorization for sensitive operations:**
```python
# Verify post ownership before deletion
post = cursor.fetchone()
if post[6] != session["userName"] and session.get("role") != "admin":
    flashMessage("error", translations["unauthorized"])
    return redirect("/")
```

### Input Validation

**Use WTForms validators:**
```python
from wtforms.validators import DataRequired, Email, Length, Regexp

class SignUpForm(FlaskForm):
    userName = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=20),
            Regexp(r'^[a-zA-Z0-9_]+$', message="Only alphanumeric")
        ]
    )
```

**Validate file uploads:**
```python
from utils.fileUploadValidator import FileUploadValidator

if not FileUploadValidator.validateFile(file, ["jpg", "png", "webp"]):
    flashMessage("error", translations["invalidFileType"])
    return redirect(request.path)
```

### XSS Prevention

**Markdown sanitization:**
```python
from utils.markdown_renderer import render_markdown

# Automatically sanitizes with bleach
safe_html = render_markdown(user_markdown)
```

**Template auto-escaping:**
```jinja2
{# Jinja2 auto-escapes by default #}
{{ userContent }}

{# Only use |safe for pre-sanitized content #}
{{ sanitizedMarkdown|safe }}
```

### CSRF Protection

**All forms must include CSRF token:**
```jinja2
<form method="POST">
    {{ form.csrf_token }}
    <!-- Form fields -->
</form>
```

**AJAX requests:**
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

### Rate Limiting

**Applied automatically to login route:**
```python
from utils.rateLimiter import RateLimiter

# Check rate limit
rate_limiter = RateLimiter(request.remote_addr, request.headers.get('User-Agent', ''))
if rate_limiter.is_rate_limited():
    return render_template("login.html", error="tooManyAttempts")
```

### File Upload Security

**Validation checklist:**
```python
from utils.fileUploadValidator import FileUploadValidator

# 1. Check file exists
if not file:
    return error

# 2. Validate file type and content
if not FileUploadValidator.validateFile(file, ["jpg", "png", "webp"]):
    return error

# 3. Check file size
if file.content_length > Settings.MAX_UPLOAD_SIZE:
    return error

# 4. Sanitize filename (handled by validator)
```

### Redirect Validation

**Prevent open redirects:**
```python
from utils.redirectValidator import RedirectValidator

redirect_url = request.args.get("redirect", "/")
safe_url = RedirectValidator.validate(redirect_url, request.host_url)
return redirect(safe_url)
```

---

## Common Tasks

### 1. Creating a New Post Type

**Example: Adding "Tutorial" post type**

1. Update category list in settings
2. Add translation keys
3. Update createPost.py dropdown
4. No database changes needed

### 2. Adding Admin Panel Feature

**Example: User activity log viewer**

1. Create `routes/adminPanelActivity.py`
2. Add admin role check
3. Create template in `templates/adminPanelActivity.html`
4. Register blueprint in app.py

### 3. Implementing New Analytics

**Example: Track referrer URLs**

1. Update `postsAnalytics` schema in dbChecker.py
2. Modify post.py to capture referrer
3. Update analytics display in postsAnalytics.py
4. Add chart rendering in postsAnalytics.js

### 4. Custom Email Templates

**Example: Welcome email**

1. Create email template function
2. Use SMTP settings from Settings class
3. Call in signup route after user creation

### 5. Adding Security Headers

**Already implemented in app.py after_request:**
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # ... more headers
    return response
```

---

## Testing Strategy

### Current Status

**No automated tests currently exist** - this is a recommended improvement area.

### Recommended Testing Approach

**1. Unit Tests for Utilities:**
```python
# tests/test_validators.py
import pytest
from app.utils.redirectValidator import RedirectValidator

def test_redirect_validator_blocks_external():
    result = RedirectValidator.validate(
        "https://evil.com",
        "https://localhost:1283"
    )
    assert result == "/"

def test_redirect_validator_allows_relative():
    result = RedirectValidator.validate("/dashboard", "https://localhost:1283")
    assert result == "/dashboard"
```

**2. Integration Tests for Routes:**
```python
# tests/test_routes.py
import pytest
from app.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_rate_limiting(client):
    for i in range(6):
        response = client.post('/login', data={
            'userName': 'test',
            'password': 'wrong'
        })
    assert b'too many attempts' in response.data.lower()
```

**3. Security Tests:**
- CSRF token validation
- SQL injection attempts
- XSS payload filtering
- File upload restrictions
- Open redirect prevention

### Manual Testing Checklist

From README.md:
- [ ] Login rate limiting (5 attempts → lockout)
- [ ] File upload rejection (invalid types)
- [ ] File size limits enforced
- [ ] Open redirects blocked
- [ ] CSRF tokens validated
- [ ] Session expires after 1 hour
- [ ] Admin panel requires admin role
- [ ] Users can only delete own content

---

## Debugging & Troubleshooting

### Logging

**Tamga logger usage:**
```python
from utils.log import Log

Log().info("Information message")
Log().success("Success message")
Log().warning("Warning message")
Log().error("Error message")
```

**Log output location:**
- Console (colored output)
- `app/logs/` directory (if enabled)

### Common Issues

**1. "SMTP credentials not configured"**
```bash
# Add to .env
SMTP_PASSWORD=your-password
SMTP_MAIL=your-email@example.com
```

**2. "Permission denied on database files"**
```bash
./scripts/fix_permissions.sh
```

**3. "Rate limit triggered"**
```sql
-- Clear failed attempts
DELETE FROM login_attempts WHERE identifier LIKE '%username%';
```

**4. "Session expires too quickly"**
```env
# Increase session lifetime in .env
PERMANENT_SESSION_LIFETIME=7200  # 2 hours
```

### Debug Mode

**Enable only for development:**
```env
DEBUG_MODE=True  # NEVER use in production!
```

**Debug features:**
- Detailed error pages
- Auto-reload on code changes
- Stack traces in browser

### Database Inspection

```bash
# Connect to SQLite
sqlite3 app/db/users.db

# Useful queries
.tables
.schema Users
SELECT * FROM Users WHERE userName = 'admin';
.quit
```

---

## Deployment Considerations

### Pre-Deployment Checklist

From SECURITY.md:
- [ ] Set `DEBUG_MODE=False` in `.env`
- [ ] Generate strong `APP_SECRET_KEY`
- [ ] Configure SMTP credentials
- [ ] Set `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- [ ] Run `./scripts/fix_permissions.sh`
- [ ] Configure HTTPS/TLS on web server
- [ ] Enable reCAPTCHA (optional but recommended)
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Change default admin password

### Production Configuration

**Environment variables:**
```env
DEBUG_MODE=False
SESSION_COOKIE_SECURE=True
PERMANENT_SESSION_LIFETIME=3600
RATE_LIMIT_ENABLED=True
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900
```

### Security Headers

**Already configured in app.py:**
- Content-Security-Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security (HSTS)
- Referrer-Policy: strict-origin-when-cross-origin

### Database Backups

**Recommended backup strategy:**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
cp app/db/*.db backups/backup_$DATE/
```

### Monitoring

**Key metrics to monitor:**
- Failed login attempts
- File upload sizes/types
- Database query performance
- Session activity
- Admin actions

---

## Advanced Topics

### Internationalization (i18n)

**Supported languages:** English, Turkish, Spanish, German, Chinese, French, Ukrainian, Russian, Portuguese, Japanese, Polish, Hindi

**Adding a new language:**
1. Create `translations/xx.json` (xx = language code)
2. Copy structure from `translations/en.json`
3. Translate all keys
4. Add language to `Settings.LANGUAGES` list
5. Add language option in `components/navbar.html`

### Theme System

**35 DaisyUI themes available:**
```javascript
// Set theme via JavaScript
document.documentElement.setAttribute('data-theme', 'dark');
```

**Theme stored in session:**
```python
session["theme"] = request.form.get("theme", "light")
```

### Custom Middleware

**Before request hooks:**
```python
# utils/beforeRequest/customHook.py
from flask import session

def customBeforeRequest():
    # Logic runs before every request
    pass

# Register in app.py
app.before_request(customBeforeRequest)
```

**After request hooks:**
```python
@app.after_request
def customAfterRequest(response):
    # Logic runs after every request
    return response
```

### File Upload Handling

**FileUploadValidator features:**
- Extension whitelist
- MIME type validation
- File size limits
- Content verification (prevents fake extensions)
- Filename sanitization

### Markdown Rendering

**Supported features:**
- Code blocks with syntax highlighting
- Tables
- Task lists
- Strikethrough
- Links (safe protocols only)
- Images
- Headers
- Blockquotes

**Security:**
- Bleach sanitization
- Allowed HTML tags whitelist
- URL protocol validation

---

## Key File References

### Most Important Files

| File | Path | Purpose |
|------|------|---------|
| Main App | `app/app.py:1` | Application entry point & configuration |
| Settings | `app/settings.py:1` | Environment & feature configuration |
| DB Schema | `app/utils/dbChecker.py:1` | Database schema initialization |
| Rate Limiter | `app/utils/rateLimiter.py:1` | Brute force protection |
| File Validator | `app/utils/fileUploadValidator.py:1` | Upload security |
| Redirect Validator | `app/utils/redirectValidator.py:1` | Open redirect prevention |
| Token Manager | `app/utils/secureTokenManager.py:1` | Password reset tokens |
| Markdown Renderer | `app/utils/markdown_renderer.py:1` | Safe markdown to HTML |
| Login Route | `app/routes/login.py:1` | Authentication logic |
| Create Post | `app/routes/createPost.py:1` | Post creation |
| Admin Panel | `app/routes/adminPanel.py:1` | Admin dashboard |

### Security-Critical Files

**Always review these when making changes:**
- `app/utils/rateLimiter.py` - Rate limiting
- `app/utils/fileUploadValidator.py` - File uploads
- `app/utils/redirectValidator.py` - Redirect validation
- `app/routes/login.py` - Authentication
- `app/routes/adminPanel*.py` - Authorization
- `app/utils/delete.py` - Ownership checks

---

## Best Practices for AI Assistants

### When Making Changes

1. **Always read the file first** before editing
2. **Preserve existing patterns** (blueprint structure, error handling)
3. **Add security checks** for user input and authorization
4. **Use parameterized queries** for all database operations
5. **Include docstrings** for new functions
6. **Update translations** if adding user-facing text
7. **Test CSRF protection** on new forms
8. **Log significant actions** using Tamga logger
9. **Follow PEP 8** style guidelines
10. **Check for similar code** before creating new utilities

### Security Mindset

**Always ask:**
- Does this accept user input? → Validate it
- Does this access the database? → Use parameterized queries
- Does this require authentication? → Check session
- Does this require authorization? → Verify ownership/role
- Does this redirect? → Validate the URL
- Does this upload files? → Validate type, size, content
- Does this render user content? → Sanitize/escape it
- Does this use CSRF-protected forms? → Include token

### Code Review Checklist

Before proposing changes:
- [ ] Code follows existing patterns
- [ ] Security checks in place
- [ ] Error handling implemented
- [ ] Logging added for debugging
- [ ] Translations updated (if applicable)
- [ ] No hardcoded credentials
- [ ] Database connections closed
- [ ] CSRF protection on forms
- [ ] Input validation present
- [ ] Authorization checks added

---

## Troubleshooting Guide

### Common Error Messages

**"Invalid CSRF token"**
- Ensure form includes `{{ form.csrf_token }}`
- Check AJAX requests include X-CSRFToken header
- Verify session is active

**"Database is locked"**
- Another process has database open
- Check for unclosed connections
- Restart application

**"Account locked"**
- Too many failed login attempts
- Wait 15 minutes or clear login_attempts table
- Check rate limiter configuration

**"Invalid file type"**
- File extension not in whitelist
- File content doesn't match extension
- Check FileUploadValidator.validateFile() call

### Performance Issues

**Slow page loads:**
- Check database query efficiency
- Review pagination implementation
- Verify file sizes aren't excessive

**High memory usage:**
- Ensure database connections are closed
- Check for memory leaks in long-running processes
- Review file upload handling

---

## Resources & Documentation

### Official Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [WTForms](https://wtforms.readthedocs.io/)
- [Tailwind CSS](https://tailwindcss.com/)
- [DaisyUI](https://daisyui.com/)

### Project Documentation
- `README.md` - Getting started guide
- `SECURITY.md` - Comprehensive security documentation
- `SECURITY_FIXES.md` - Security changelog
- `.env.example` - Configuration reference

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)

---

## Contributing Guidelines

### Code Quality Standards

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Use parameterized queries for database operations
- Validate all user inputs
- Add security checks for sensitive operations
- Include error handling
- Log significant actions

### Pull Request Checklist

- [ ] Code follows project conventions
- [ ] Security considerations addressed
- [ ] No hardcoded credentials
- [ ] Translations updated (if applicable)
- [ ] Documentation updated (if applicable)
- [ ] Manual testing completed
- [ ] No debug code left in

### Security Vulnerability Reporting

**Do NOT open public issues for security vulnerabilities!**

1. Email maintainer privately
2. Include detailed description and reproduction steps
3. Allow 90 days for patch development
4. Coordinate public disclosure timing

---

## Changelog

### Version 3.0.0dev (Current)

**18 Security Vulnerabilities Fixed:**
- ✅ Removed hardcoded credentials
- ✅ Added file upload validation
- ✅ Implemented open redirect protection
- ✅ Added rate limiting & account lockout
- ✅ Enhanced session security
- ✅ Added comprehensive security headers
- ✅ Implemented authorization checks
- ✅ Fixed username enumeration
- ✅ Secured database file permissions
- ✅ Added secure token management (infrastructure)

**See:** `SECURITY_FIXES.md` for detailed changelog

---

## Contact & Support

**Issues:** [GitHub Issues](https://github.com/DogukanUrker/flaskBlog/issues)
**Discussions:** [GitHub Discussions](https://github.com/DogukanUrker/flaskBlog/discussions)
**Author:** Doğukan Ürker - [dogukanurker.com](https://dogukanurker.com)
**Email:** dogukanurker@icloud.com

---

**Last Updated:** 2025-11-18
**Maintained By:** AI Assistant (Claude)
**License:** MIT
