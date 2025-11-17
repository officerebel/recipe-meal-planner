# Railway Deployment Guide

This guide walks you through deploying the Django + Quasar blueprint to Railway.

## 🚀 Quick Deployment

### 1. Prerequisites
- Railway account ([sign up here](https://railway.app))
- Railway CLI installed (`npm install -g @railway/cli`)
- Git repository with your code

### 2. Initial Setup
```bash
# Login to Railway
railway login

# Initialize project
railway init

# Link to existing project (optional)
railway link [project-id]
```

### 3. Deploy Backend (Django)
```bash
# Navigate to backend directory
cd backend

# Deploy backend service
railway up

# Set environment variables
railway variables set SECRET_KEY="your-secret-key-here"
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=".railway.app"

# Add PostgreSQL database
railway add postgresql
```

### 4. Deploy Frontend (Quasar)
```bash
# Navigate to frontend directory  
cd ../frontend

# Deploy frontend service
railway up

# Set environment variables
railway variables set API_BASE_URL="https://your-backend.railway.app/api"
```

## 🔧 Environment Variables

### Backend Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-xyz...` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `.railway.app,localhost` |
| `DATABASE_URL` | Database URL | Auto-provided by Railway |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `https://frontend.railway.app` |

### Frontend Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `https://backend.railway.app/api` |

## 🗄️ Database Setup

Railway automatically provides PostgreSQL when you add it:

```bash
# Add PostgreSQL to your project
railway add postgresql

# Run migrations
railway run python manage.py migrate

# Create superuser (optional)
railway run python manage.py createsuperuser
```

## 🔄 Automatic Deployments

Set up automatic deployments from GitHub:

1. Connect your GitHub repository in Railway dashboard
2. Enable auto-deployments on push to main branch
3. Configure build and deploy commands in `railway.json`

## 🏥 Health Checks

Both services include health check endpoints:

- **Backend**: `/health/` - Returns JSON status
- **Frontend**: `/` - Returns the main app

## 🔍 Monitoring

Monitor your deployments:

```bash
# View logs
railway logs

# Check service status
railway status

# View metrics in dashboard
railway open
```

## 🛠️ Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
   - Check that both services are deployed

2. **Database Connection**
   - Verify `DATABASE_URL` is set automatically
   - Run migrations: `railway run python manage.py migrate`

3. **Static Files**
   - Ensure `STATIC_ROOT` is configured
   - Run: `railway run python manage.py collectstatic`

4. **Build Failures**
   - Check `railway.json` configuration
   - Verify all dependencies in requirements.txt/package.json

### Debug Commands
```bash
# Check environment variables
railway variables

# Run Django shell
railway run python manage.py shell

# Check database
railway run python manage.py dbshell

# View recent deployments
railway deployments
```

## 📈 Scaling

Railway automatically scales based on usage. For custom scaling:

1. Go to Railway dashboard
2. Select your service
3. Configure scaling settings
4. Set resource limits if needed

## 🔒 Security

Production security checklist:

- [ ] Set strong `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up CORS correctly
- [ ] Use HTTPS (automatic on Railway)
- [ ] Regular dependency updates

## 💰 Pricing

Railway offers:
- **Hobby Plan**: $5/month with usage-based pricing
- **Pro Plan**: $20/month with higher limits
- **Free Trial**: Limited resources for testing

Monitor usage in the Railway dashboard to avoid unexpected charges.