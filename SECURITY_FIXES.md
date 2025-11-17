# Security Fixes Summary

This document provides a quick overview of the security improvements made to FlaskBlog.

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```env
   SMTP_PASSWORD=your-password
   APP_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
   ```

3. **Fix file permissions:**
   ```bash
   chmod +x scripts/fix_permissions.sh
   ./scripts/fix_permissions.sh
   ```

4. **Run the application:**
   ```bash
   cd app
   uv run app.py
   ```

## What Was Fixed

### 🔴 Critical (Fixed)
1. **Hardcoded SMTP Password** → Now uses environment variables
2. **Unrestricted File Uploads** → Validates type, size, and content
3. **Open Redirect Vulnerability** → Validates all redirect URLs

### 🟠 High (Fixed)
4. **No Rate Limiting** → 5 attempts max, 15-minute lockout
5. **Weak Session Secret** → Persistent secure key
6. **Missing Authorization** → Delete operations verify ownership
7. **Username Enumeration** → Generic "Invalid credentials" message
8. **No Account Lockout** → Implemented with rate limiter

### 🟡 Medium (Fixed)
9. **Debug Mode On** → Defaults to False
10. **Missing Security Headers** → Added CSP, X-Frame-Options, HSTS, etc.
11. **Database Permissions** → Changed to 600 (owner only)
12. **Weak Session Config** → HttpOnly, Secure, SameSite cookies

## New Security Features

### File Upload Validation
- **Max size:** 5MB (configurable)
- **Allowed types:** JPG, PNG, WebP only
- **Content validation:** Checks actual file type, not just extension
- **Filename sanitization:** Prevents directory traversal

### Rate Limiting
- **5 failed login attempts** → 15-minute lockout
- Tracks by IP + username
- Automatic cleanup of old records

### Security Headers
```
Content-Security-Policy: Strict resource loading
X-Frame-Options: DENY (prevents clickjacking)
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: HSTS for HTTPS
```

### Session Security
- **Secure cookies** (HTTPS only when enabled)
- **HttpOnly** (prevents XSS access)
- **SameSite=Lax** (CSRF protection)
- **1-hour timeout**

## Files Created

```
app/utils/fileUploadValidator.py    - File upload validation
app/utils/redirectValidator.py       - Redirect URL validation
app/utils/rateLimiter.py             - Rate limiting & lockout
app/utils/secureTokenManager.py      - Password reset tokens (ready)
scripts/fix_permissions.sh           - Fix file permissions
.env.example                         - Environment template
SECURITY.md                          - Comprehensive security docs
```

## Files Modified

```
app/settings.py              - Environment variable support
app/app.py                   - Security headers, session config
app/routes/login.py          - Rate limiting, no enumeration
app/routes/createPost.py     - File validation
app/routes/editPost.py       - File validation
app/utils/delete.py          - Authorization checks
.gitignore                   - Added .secret_key
```

## Configuration

All security settings in `.env`:

```env
# Required
SMTP_PASSWORD=your-password
APP_SECRET_KEY=generate-with-secrets-module

# Optional (with defaults)
DEBUG_MODE=False
MAX_UPLOAD_SIZE=5242880
ALLOWED_UPLOAD_EXTENSIONS=jpg,jpeg,png,webp
RATE_LIMIT_ENABLED=True
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900
SESSION_COOKIE_SECURE=False  # Set True with HTTPS
```

## Testing

### Test Rate Limiting
Try 6 failed logins → Should see lockout message

### Test File Upload
Try uploading .php file → Should reject

### Test Open Redirect
Visit `/login/redirect=https:&&evil.com` → Should redirect to `/`

## Production Deployment

Before going live:

1. ✅ Set `DEBUG_MODE=False`
2. ✅ Generate new `APP_SECRET_KEY`
3. ✅ Configure SMTP credentials
4. ✅ Enable `SESSION_COOKIE_SECURE=True` (requires HTTPS)
5. ✅ Run `./scripts/fix_permissions.sh`
6. ✅ Set up HTTPS/TLS
7. ✅ Enable reCAPTCHA (optional but recommended)
8. ✅ Configure database backups
9. ✅ Set up log rotation
10. ✅ Test all functionality

## Remaining Recommendations

### To Integrate Later
- [ ] Complete password reset with secure tokens (infrastructure ready)
- [ ] Add regex validation for usernames
- [ ] Implement 2FA/TOTP
- [ ] Add security.txt file
- [ ] Set up dependency scanning
- [ ] Implement CSP reporting endpoint

### Monitoring
- Monitor failed login attempts in logs
- Track rate limit triggers
- Review file upload patterns
- Audit admin actions

## Breaking Changes

⚠️ **Important:**
- SMTP credentials must now be in environment variables
- Default debug mode is now `False`
- Database files have restricted permissions (may need sudo to access)
- Session cookies may require HTTPS in production

## Support

For detailed documentation, see [SECURITY.md](SECURITY.md)

For issues, check existing security measures don't conflict with your deployment.

---

**Security Version:** 1.0.0
**Last Updated:** 2025-11-17
