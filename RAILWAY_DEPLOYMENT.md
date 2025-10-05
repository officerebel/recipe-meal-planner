# Railway Deployment Guide

This guide covers deploying both the Django backend and Quasar frontend to Railway.

## Prerequisites

1. Railway account (https://railway.app)
2. Railway CLI installed: `npm install -g @railway/cli`
3. Git repository with your code

## Backend Deployment (Django)

### 1. Create Backend Service

```bash
# Login to Railway
railway login

# Create new project
railway new

# Deploy backend from root directory
railway up
```

### 2. Environment Variables

Set these environment variables in Railway dashboard:

```
RAILWAY_ENVIRONMENT=production
DATABASE_URL=<automatically provided by Railway PostgreSQL>
SECRET_KEY=<generate a secure secret key>
DEFAULT_FROM_EMAIL=Recipe Meal Planner <noreply@yourapp.com>
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<your email>
EMAIL_HOST_PASSWORD=<your app password>
SITE_URL=https://your-frontend-domain.railway.app
```

### 3. Add PostgreSQL Database

1. Go to Railway dashboard
2. Click "Add Service" → "Database" → "PostgreSQL"
3. Railway will automatically set DATABASE_URL

### 4. Backend Configuration

The backend is already configured with:
- ✅ `railway.json` with proper build/deploy commands
- ✅ Health check endpoint at `/api/health/`
- ✅ Production settings for Railway environment
- ✅ WhiteNoise for static files
- ✅ CORS configuration
- ✅ PostgreSQL support

## Frontend Deployment (Quasar)

### 1. Update Backend URL

Update the backend URL in `quasar-project/src/boot/axios.js`:

```javascript
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production'
    ? 'https://YOUR-BACKEND-DOMAIN.railway.app/api'  // Update this
    : 'http://localhost:8000/api',
  // ... rest of config
})
```

### 2. Create Frontend Service

```bash
# Navigate to frontend directory
cd quasar-project

# Create new Railway service
railway new

# Deploy frontend
railway up
```

### 3. Frontend Configuration

The frontend is already configured with:
- ✅ `railway.json` with Quasar build commands
- ✅ Production-ready build process
- ✅ Health check endpoint
- ✅ Static file serving with `serve`

## Deployment Steps

### Step 1: Deploy Backend

1. **Create backend service:**
   ```bash
   railway new recipe-meal-planner-backend
   railway up
   ```

2. **Add PostgreSQL database:**
   - In Railway dashboard, click "Add Service" → "Database" → "PostgreSQL"

3. **Set environment variables:**
   ```bash
   railway variables set SECRET_KEY="your-secret-key-here"
   railway variables set DEFAULT_FROM_EMAIL="Recipe Meal Planner <noreply@yourapp.com>"
   ```

4. **Note the backend URL** (e.g., `https://recipe-backend-production.up.railway.app`)

### Step 2: Deploy Frontend

1. **Update axios configuration** with backend URL:
   ```bash
   # Edit quasar-project/src/boot/axios.js
   # Replace 'https://proud-mercy-production.up.railway.app/api' with your actual backend URL
   ```

2. **Deploy frontend:**
   ```bash
   cd quasar-project
   railway new recipe-meal-planner-frontend
   railway up
   ```

3. **Update CORS settings** in backend:
   ```bash
   # Add your frontend URL to CORS_ALLOWED_ORIGINS in Django settings
   railway variables set SITE_URL="https://your-frontend-domain.railway.app"
   ```

## Post-Deployment

### 1. Run Migrations

```bash
# Connect to backend service
railway shell

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Create sample data (optional)
python manage.py create_sample_data
```

### 2. Test Deployment

1. **Backend health check:** `https://your-backend-domain.railway.app/api/health/`
2. **Frontend:** `https://your-frontend-domain.railway.app`
3. **API docs:** `https://your-backend-domain.railway.app/api/docs/`

### 3. Update CORS Settings

Update the Django settings with your actual frontend domain:

```python
# In settings.py, update CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = [
    "https://your-actual-frontend-domain.railway.app",
]
```

## Monitoring

- **Railway Dashboard:** Monitor deployments, logs, and metrics
- **Health Checks:** Both services have health check endpoints
- **Logs:** Use `railway logs` to view application logs

## Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Ensure frontend domain is in CORS_ALLOWED_ORIGINS
   - Check that SITE_URL environment variable is set

2. **Database Connection:**
   - Verify DATABASE_URL is set automatically by Railway
   - Run migrations after database setup

3. **Static Files:**
   - Backend uses WhiteNoise for static files
   - Run `python manage.py collectstatic` if needed

4. **Build Failures:**
   - Check Railway build logs
   - Ensure all dependencies are in requirements.txt/package.json

### Useful Commands

```bash
# View logs
railway logs

# Connect to service shell
railway shell

# Check environment variables
railway variables

# Redeploy
railway up --detach
```

## Security Notes

- ✅ DEBUG=False in production
- ✅ Secure SSL settings enabled
- ✅ HSTS headers configured
- ✅ Secret key from environment variable
- ✅ Database credentials managed by Railway
- ✅ CORS properly configured

## Features Available After Deployment

- ✅ Recipe management with PDF import
- ✅ Meal planning and scheduling
- ✅ Shopping list generation and export
- ✅ Family management and sharing
- ✅ User authentication and profiles
- ✅ Mobile-responsive design
- ✅ API documentation at `/api/docs/`

Your Recipe Meal Planner is now ready for production use!