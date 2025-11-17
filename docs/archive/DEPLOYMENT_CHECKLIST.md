# Railway Deployment Checklist

## Pre-Deployment ✅

- [x] Railway CLI installed (`npm install -g @railway/cli`)
- [x] Logged into Railway (`railway login`)
- [x] Backend `railway.json` configured
- [x] Frontend `railway.json` configured
- [x] Django settings configured for production
- [x] Health check endpoints created
- [x] Requirements.txt includes all dependencies

## Backend Deployment

### 1. Deploy Backend Service
```bash
# From project root directory
railway up
```

### 2. Add Database
- [ ] Go to Railway dashboard
- [ ] Click "Add Service" → "Database" → "PostgreSQL"
- [ ] Wait for DATABASE_URL to be automatically set

### 3. Set Environment Variables
```bash
railway variables set SECRET_KEY="your-secure-secret-key-here"
railway variables set DEFAULT_FROM_EMAIL="Recipe Meal Planner <noreply@yourapp.com>"
railway variables set EMAIL_HOST="smtp.gmail.com"
railway variables set EMAIL_PORT="587"
railway variables set EMAIL_HOST_USER="your-email@gmail.com"
railway variables set EMAIL_HOST_PASSWORD="your-app-password"
```

### 4. Run Initial Setup
```bash
railway shell
python manage.py migrate
python manage.py createsuperuser  # Optional
python manage.py create_sample_data  # Optional
exit
```

### 5. Test Backend
- [ ] Health check: `https://your-backend.railway.app/api/health/`
- [ ] API docs: `https://your-backend.railway.app/api/docs/`
- [ ] Admin panel: `https://your-backend.railway.app/admin/`

## Frontend Deployment

### 1. Update Backend URL
- [ ] Edit `quasar-project/src/boot/axios.js`
- [ ] Replace backend URL with your Railway backend URL
- [ ] Commit changes

### 2. Deploy Frontend Service
```bash
cd quasar-project
railway up
```

### 3. Test Frontend
- [ ] Frontend loads: `https://your-frontend.railway.app`
- [ ] Can register/login
- [ ] Can create recipes
- [ ] Can import PDFs
- [ ] Can create meal plans

## Post-Deployment Configuration

### 1. Update CORS Settings
- [ ] Add frontend URL to Django CORS_ALLOWED_ORIGINS
- [ ] Set SITE_URL environment variable to frontend URL

### 2. Update Environment Variables
```bash
railway variables set SITE_URL="https://your-frontend.railway.app"
```

### 3. Final Tests
- [ ] Recipe creation works
- [ ] PDF import works
- [ ] Meal planning works
- [ ] Shopping lists work
- [ ] Family management works
- [ ] Mobile responsiveness works

## URLs to Save

- **Backend:** `https://your-backend.railway.app`
- **Frontend:** `https://your-frontend.railway.app`
- **API Docs:** `https://your-backend.railway.app/api/docs/`
- **Admin:** `https://your-backend.railway.app/admin/`

## Quick Commands

```bash
# View logs
railway logs

# Connect to backend shell
railway shell

# Check status
railway status

# Redeploy
railway up --detach

# View environment variables
railway variables
```

## Troubleshooting

### Common Issues:
1. **CORS errors:** Check CORS_ALLOWED_ORIGINS includes frontend URL
2. **Database errors:** Ensure migrations are run after adding PostgreSQL
3. **Build failures:** Check Railway logs for specific errors
4. **Static files:** WhiteNoise handles static files automatically

### Support:
- Railway docs: https://docs.railway.app
- Project documentation: See README.md and other docs

---

## ✅ Deployment Complete!

Your Recipe Meal Planner is now live and ready for users!