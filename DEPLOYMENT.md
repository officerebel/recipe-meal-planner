# Railway Deployment Guide

This guide will help you deploy your Recipe & Meal Planner application to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Railway CLI** (optional): Install with `npm install -g @railway/cli`

## Deployment Steps

### 1. Create Railway Projects

You'll need to deploy the backend and frontend as separate services:

#### Backend Deployment

1. **Create New Project**: Go to Railway dashboard and click "New Project"
2. **Deploy from GitHub**: Select "Deploy from GitHub repo"
3. **Select Repository**: Choose your repository
4. **Configure Service**:
   - **Root Directory**: `backend`
   - **Build Command**: Automatically detected from `railway.json`
   - **Start Command**: Automatically detected from `railway.json`

#### Frontend Deployment

1. **Add Service**: In the same project, click "Add Service" → "GitHub Repo"
2. **Configure Service**:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Start Command**: `npx serve dist/spa -s -l $PORT`

### 2. Environment Variables

#### Backend Environment Variables

Set these in your Railway backend service:

```bash
# Required
SECRET_KEY=your-super-secret-django-key-here
DATABASE_URL=postgresql://... # Railway will provide this automatically

# Optional but recommended
DEBUG=False
ALLOWED_HOSTS=.railway.app
SITE_URL=https://your-frontend-url.railway.app

# Email settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Recipe Planner <noreply@yourapp.com>
```

#### Frontend Environment Variables

Set these in your Railway frontend service:

```bash
VITE_API_BASE_URL=https://your-backend-url.railway.app
NODE_ENV=production
```

### 3. Database Setup

Railway will automatically provision a PostgreSQL database for your backend service. The `DATABASE_URL` environment variable will be set automatically.

### 4. Domain Configuration

1. **Backend**: Copy the Railway-provided URL (e.g., `https://backend-production-xxxx.up.railway.app`)
2. **Frontend**: Update the `VITE_API_BASE_URL` environment variable with your backend URL
3. **Custom Domains** (optional): You can add custom domains in Railway settings

### 5. Post-Deployment Steps

After successful deployment:

1. **Run Migrations**: Railway will automatically run migrations on deploy
2. **Create Superuser**: Use Railway's terminal to create an admin user:
   ```bash
   python manage.py createsuperuser
   ```
3. **Test API**: Visit `https://your-backend-url.railway.app/api/docs/` to test the API
4. **Test Frontend**: Visit your frontend URL to ensure it connects to the backend

## File Structure for Railway

Your project is already configured with the necessary files:

```
├── railway.json                 # Root Railway config
├── nixpacks.toml               # Build configuration
├── backend/
│   ├── railway.json            # Backend-specific config
│   ├── Procfile               # Alternative start command
│   ├── requirements.txt       # Python dependencies
│   └── manage.py              # Django management
├── frontend/
│   ├── railway.json           # Frontend-specific config
│   ├── package.json           # Node.js dependencies
│   └── .env.production        # Production environment
└── DEPLOYMENT.md              # This guide
```

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check that all dependencies are in `requirements.txt` and `package.json`
   - Verify Python/Node versions in Railway logs

2. **Database Connection Issues**:
   - Ensure `psycopg2-binary` is in `requirements.txt`
   - Check that `DATABASE_URL` environment variable is set

3. **Static Files Not Loading**:
   - Verify `STATIC_ROOT` and `STATICFILES_DIRS` in Django settings
   - Check that `collectstatic` runs during deployment

4. **CORS Issues**:
   - Update `CORS_ALLOWED_ORIGINS` in Django settings
   - Add your frontend domain to allowed origins

### Useful Commands

```bash
# View logs
railway logs

# Connect to database
railway connect

# Run Django commands
railway run python manage.py createsuperuser
railway run python manage.py migrate

# Deploy specific service
railway up --service backend
railway up --service frontend
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to your repository
2. **SECRET_KEY**: Generate a new secret key for production
3. **DEBUG**: Always set `DEBUG=False` in production
4. **ALLOWED_HOSTS**: Restrict to your actual domains
5. **HTTPS**: Railway provides HTTPS by default

## Monitoring

- **Railway Dashboard**: Monitor deployments, logs, and metrics
- **Health Checks**: Backend includes `/api/health/` endpoint
- **Error Tracking**: Consider adding Sentry for error monitoring

## Scaling

Railway automatically handles:
- **Auto-scaling**: Based on traffic
- **Load balancing**: Across multiple instances
- **Database backups**: Automatic PostgreSQL backups

For high-traffic applications, consider:
- **CDN**: For static files and media
- **Redis**: For caching and sessions
- **Separate database**: For production workloads