# 12-Factor App Implementation

This document describes how the Recipe Meal Planner follows the [12-Factor App](https://12factor.net) methodology for building modern, scalable web applications.

## Overview

The 12-Factor App is a methodology for building software-as-a-service apps that:
- Use declarative formats for setup automation
- Have a clean contract with the underlying operating system
- Are suitable for deployment on modern cloud platforms
- Minimize divergence between development and production
- Can scale up without significant changes

## Implementation Status

### ✅ I. Codebase
**One codebase tracked in revision control, many deploys**

- ✅ Single Git repository
- ✅ Multiple environments (development, production)
- ✅ Same codebase deployed to Railway (backend + frontend)

```bash
# Repository structure
food_app/
├── backend/          # Django backend
├── frontend/         # Quasar frontend
└── .git/            # Single version control
```

### ✅ II. Dependencies
**Explicitly declare and isolate dependencies**

**Backend (Python):**
```bash
# requirements.txt explicitly lists all dependencies
Django==5.2.7
djangorestframework==3.16.1
gunicorn==21.2.0
# ... etc
```

**Frontend (Node.js):**
```json
// package.json explicitly lists all dependencies
{
  "dependencies": {
    "quasar": "^2.16.0",
    "vue": "3.5.20",
    "axios": "^1.12.2"
  }
}
```

**Isolation:**
- Backend: Python virtual environment
- Frontend: node_modules
- Docker containers for deployment

### ⚠️ III. Config
**Store config in the environment**

**Current Status:** Partially implemented

**✅ Implemented:**
```python
# backend/recipe_meal_planner/settings.py
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
DATABASE_URL = os.environ.get('DATABASE_URL')
```

**❌ Needs Improvement:**
- Some config still hardcoded in settings.py
- Frontend API URL partially hardcoded

**TODO:**
```python
# Move all config to environment variables
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
```

### ✅ IV. Backing Services
**Treat backing services as attached resources**

**Current Implementation:**
- PostgreSQL database via DATABASE_URL
- AWS S3 for media storage (configurable)
- Can switch between SQLite (dev) and PostgreSQL (prod)

```python
# Database as attached resource
if 'DATABASE_URL' in os.environ:
    DATABASES = {'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))}
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', ...}}
```

### ✅ V. Build, Release, Run
**Strictly separate build and run stages**

**Build Stage (Railway):**
```dockerfile
# Frontend Dockerfile
RUN npm install          # Install dependencies
RUN npm run build        # Build static assets
```

**Release Stage:**
- Git commit triggers new deployment
- Railway builds Docker image
- Version tagged with git commit hash

**Run Stage:**
```dockerfile
CMD ["/start.sh"]        # Run the application
```

### ⚠️ VI. Processes
**Execute the app as one or more stateless processes**

**Current Status:** Mostly stateless

**✅ Stateless:**
- No session data stored in memory
- Database for persistent data
- S3 for file storage

**❌ Needs Improvement:**
- Shopping list cache in memory (should use Redis)
- No distributed session management

**TODO:**
```python
# Use Redis for caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}
```

### ✅ VII. Port Binding
**Export services via port binding**

**Backend:**
```python
# Gunicorn binds to PORT from environment
PORT = os.environ.get('PORT', 8000)
```

**Frontend:**
```bash
# Serve binds to PORT from environment
serve dist/spa -s -l $PORT
```

### ⚠️ VIII. Concurrency
**Scale out via the process model**

**Current Status:** Basic implementation

**✅ Implemented:**
- Gunicorn with multiple workers
- Stateless processes (can scale horizontally)

**❌ Needs Improvement:**
- No worker process separation (web vs background jobs)
- No queue system for async tasks

**TODO:**
```python
# Add Celery for background tasks
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
```

### ✅ IX. Disposability
**Maximize robustness with fast startup and graceful shutdown**

**Current Implementation:**
- Fast startup (< 10 seconds)
- Graceful shutdown via SIGTERM
- Gunicorn handles graceful worker shutdown

```python
# Gunicorn config
graceful_timeout = 30
timeout = 120
```

### ⚠️ X. Dev/Prod Parity
**Keep development, staging, and production as similar as possible**

**Current Status:** Moderate parity

**✅ Similar:**
- Same codebase
- Same dependencies
- Docker for consistency

**❌ Different:**
- Dev uses SQLite, prod uses PostgreSQL
- Dev uses local storage, prod uses S3
- Different environment variables

**TODO:**
- Use Docker Compose for local development
- Use PostgreSQL in development
- Use MinIO (S3-compatible) for local file storage

### ⚠️ XI. Logs
**Treat logs as event streams**

**Current Status:** Partially implemented

**✅ Implemented:**
```python
# Logs to stdout
LOGGING = {
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    }
}
```

**❌ Needs Improvement:**
- No structured logging (JSON format)
- No log aggregation
- Inconsistent log levels

**TODO:**
```python
# Structured logging
import structlog
logger = structlog.get_logger()
logger.info("recipe_imported", recipe_id=recipe.id, user_id=user.id)
```

### ⚠️ XII. Admin Processes
**Run admin/management tasks as one-off processes**

**Current Status:** Basic implementation

**✅ Implemented:**
```bash
# Django management commands
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

**❌ Needs Improvement:**
- No scheduled tasks (cron jobs)
- No background job processing

**TODO:**
```bash
# Use Railway cron jobs or Celery Beat
railway run python manage.py cleanup_old_data
```

## Improvement Roadmap

### Phase 1: Configuration (Priority: High)
- [ ] Move all config to environment variables
- [ ] Create .env.example file
- [ ] Document all environment variables
- [ ] Remove hardcoded values from settings.py

### Phase 2: Backing Services (Priority: High)
- [ ] Add Redis for caching
- [ ] Add Redis for session storage
- [ ] Configure connection pooling
- [ ] Add health checks for all services

### Phase 3: Processes & Concurrency (Priority: Medium)
- [ ] Add Celery for background tasks
- [ ] Separate web and worker processes
- [ ] Implement job queues
- [ ] Add process monitoring

### Phase 4: Dev/Prod Parity (Priority: Medium)
- [ ] Docker Compose for local development
- [ ] Use PostgreSQL in development
- [ ] Use MinIO for local S3
- [ ] Standardize environment setup

### Phase 5: Logging (Priority: Low)
- [ ] Implement structured logging
- [ ] Add log aggregation (e.g., Sentry)
- [ ] Standardize log levels
- [ ] Add request ID tracking

### Phase 6: Admin Processes (Priority: Low)
- [ ] Add scheduled tasks
- [ ] Implement data cleanup jobs
- [ ] Add backup automation
- [ ] Create admin CLI tools

## Environment Variables Reference

### Required Variables (Production)
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=eu-west-1

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

### Optional Variables
```bash
# Redis (future)
REDIS_URL=redis://localhost:6379/0

# Sentry (future)
SENTRY_DSN=https://...

# Railway
RAILWAY_ENVIRONMENT=production
PORT=8000
```

## Testing 12-Factor Compliance

### Checklist:
```bash
# 1. Can you deploy from a fresh clone?
git clone <repo>
cd food_app
# Set environment variables
docker-compose up

# 2. Are all dependencies declared?
pip install -r requirements.txt
npm install

# 3. Can you switch databases easily?
export DATABASE_URL=postgresql://...
python manage.py migrate

# 4. Can you scale horizontally?
railway scale --replicas 3

# 5. Are logs going to stdout?
railway logs | grep "INFO"
```

## Benefits of 12-Factor Compliance

1. **Portability**: Easy to deploy to any cloud platform
2. **Scalability**: Can scale horizontally without code changes
3. **Maintainability**: Clear separation of concerns
4. **Reliability**: Stateless processes are more robust
5. **Developer Experience**: Consistent dev/prod environments

## Resources

- [12factor.net](https://12factor.net) - Official methodology
- [Django 12-Factor](https://django-environ.readthedocs.io/) - Django-specific guide
- [Railway Docs](https://docs.railway.app/) - Deployment platform
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## Next Steps

1. Review current implementation status
2. Prioritize improvements based on roadmap
3. Implement Phase 1 (Configuration)
4. Test changes in staging environment
5. Deploy to production
6. Monitor and iterate
