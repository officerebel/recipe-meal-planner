# Environment Variables Reference

Complete reference for all environment variables used in the Recipe Meal Planner application.

## Required Variables

### Production (Railway)

```bash
# Django Core
SECRET_KEY=your-secret-key-min-50-chars
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional but Recommended
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Optional Variables

### Django Settings

```bash
# Debug Mode (default: False in production, True in development)
DEBUG=False

# Allowed Hosts (comma-separated, default: localhost,127.0.0.1,.railway.app)
ALLOWED_HOSTS=localhost,127.0.0.1,.railway.app,yourdomain.com

# CORS Origins (comma-separated)
CORS_ALLOWED_ORIGINS=http://localhost:9000,https://yourdomain.com
```

### Database

```bash
# PostgreSQL Connection (Railway auto-sets this)
DATABASE_URL=postgresql://user:password@host:5432/database

# Connection Pool Settings (optional)
DB_CONN_MAX_AGE=600
DB_CONN_HEALTH_CHECKS=True
```

### AWS S3 Storage

```bash
# AWS Credentials (optional - for media file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=eu-west-1

# Railway Volume (alternative to S3)
RAILWAY_VOLUME_MOUNT_PATH=/app/media
```

### Email Configuration

```bash
# Email Backend (optional - for password reset, invitations)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=Recipe Planner <noreply@yourapp.com>
```

### Site Configuration

```bash
# Site URL (used in emails, invitations)
SITE_URL=https://yourapp.com
```

### Railway Platform

```bash
# Auto-set by Railway
RAILWAY_ENVIRONMENT=production
RAILWAY_PROJECT_ID=xxx
RAILWAY_SERVICE_ID=xxx
PORT=8000
```

### Frontend (Quasar/Vite)

```bash
# API Base URL
VITE_API_BASE_URL=https://api.yourapp.com

# Node Environment
NODE_ENV=production
```

## Variable Types

### Boolean Variables
Accepts: `true`, `1`, `yes` (case-insensitive) = True
Everything else = False

```bash
DEBUG=true          # True
DEBUG=1             # True
DEBUG=yes           # True
DEBUG=false         # False
DEBUG=0             # False
DEBUG=anything      # False
```

### List Variables
Comma-separated values, whitespace is trimmed

```bash
ALLOWED_HOSTS=localhost,127.0.0.1,.railway.app
# Results in: ['localhost', '127.0.0.1', '.railway.app']

CORS_ALLOWED_ORIGINS=http://localhost:9000, https://app.com
# Results in: ['http://localhost:9000', 'https://app.com']
```

### Integer Variables
Must be valid integers

```bash
PORT=8000           # 8000
EMAIL_PORT=587      # 587
DB_CONN_MAX_AGE=600 # 600
```

## Environment-Specific Configurations

### Local Development

Create `.env` file in project root:

```bash
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:9000,http://localhost:3000
SITE_URL=http://localhost:9000
```

### Railway Production

Set in Railway dashboard or via CLI:

```bash
# Required
railway variables set SECRET_KEY="your-production-secret-key"
railway variables set DATABASE_URL="postgresql://..."

# Optional
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="yourdomain.com,.railway.app"
railway variables set CORS_ALLOWED_ORIGINS="https://yourdomain.com"
```

### Docker

Create `.env` file for docker-compose:

```bash
DEBUG=True
SECRET_KEY=docker-dev-key
DATABASE_URL=postgresql://postgres:postgres@db:5432/recipe_planner
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Validation

The application validates required environment variables at startup:

```python
# In settings.py
from recipe_meal_planner.config import validate_config

# Validates configuration
validate_config()
```

### Production Validation

In production, these variables are required:
- `SECRET_KEY` - Must be set and non-empty
- `DATABASE_URL` - Must be set for PostgreSQL

If missing, the application will fail to start with a clear error message.

## Security Best Practices

### ✅ DO:
- Use strong, random SECRET_KEY (min 50 characters)
- Set DEBUG=False in production
- Use environment-specific .env files
- Never commit .env files to git
- Use Railway's secret management
- Rotate secrets regularly

### ❌ DON'T:
- Hardcode secrets in code
- Use default SECRET_KEY in production
- Commit .env files
- Share production credentials
- Use DEBUG=True in production

## Troubleshooting

### Issue: "SECRET_KEY is not set"
**Solution:** Set SECRET_KEY environment variable
```bash
railway variables set SECRET_KEY="$(openssl rand -base64 50)"
```

### Issue: "ALLOWED_HOSTS validation error"
**Solution:** Add your domain to ALLOWED_HOSTS
```bash
railway variables set ALLOWED_HOSTS="yourdomain.com,.railway.app"
```

### Issue: "CORS error in browser"
**Solution:** Add frontend URL to CORS_ALLOWED_ORIGINS
```bash
railway variables set CORS_ALLOWED_ORIGINS="https://frontend.railway.app"
```

### Issue: "Database connection failed"
**Solution:** Check DATABASE_URL is set correctly
```bash
railway variables | grep DATABASE_URL
```

## Helper Functions

The application provides helper functions in `recipe_meal_planner/config.py`:

```python
from recipe_meal_planner.config import (
    get_env_bool,    # Get boolean value
    get_env_list,    # Get list value (comma-separated)
    get_env_str,     # Get string value
    get_env_int,     # Get integer value
    require_env,     # Get required value (raises if missing)
    is_production,   # Check if in production
    is_development,  # Check if in development
)

# Usage examples
DEBUG = get_env_bool('DEBUG', default=True)
ALLOWED_HOSTS = get_env_list('ALLOWED_HOSTS', default='localhost')
PORT = get_env_int('PORT', default=8000)
SECRET_KEY = require_env('SECRET_KEY')  # Raises if not set
```

## Related Documentation

- [12-Factor App Implementation](12_FACTOR_APP.md)
- [Main README](../README.md)
- [Railway Documentation](https://docs.railway.app/)
