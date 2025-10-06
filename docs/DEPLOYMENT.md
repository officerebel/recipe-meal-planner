# Recipe Meal Planner - Deployment Guide

## 🚀 Deploying to Railway

### Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))

### Step 1: Push to GitHub

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Recipe Meal Planner with family management"
   ```

2. **Create GitHub Repository**:
   - Go to [github.com](https://github.com) and create a new repository
   - Name it `recipe-meal-planner` or similar
   - Don't initialize with README (we already have one)

3. **Connect and Push**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/recipe-meal-planner.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Railway

1. **Connect Railway to GitHub**:
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `recipe-meal-planner` repository

2. **Configure Environment Variables**:
   In Railway dashboard, add these environment variables:
   ```
   RAILWAY_ENVIRONMENT=production
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=False
   ```

3. **Add PostgreSQL Database**:
   - In your Railway project, click "New Service"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically set DATABASE_URL

4. **Deploy**:
   - Railway will automatically build and deploy your app
   - The build process will run migrations and collect static files
   - Your app will be available at `https://your-app-name.railway.app`

### Step 3: Frontend Deployment (Optional)

If you want to deploy the Quasar frontend separately:

1. **Build the Frontend**:
   ```bash
   cd quasar-project
   npm install
   npm run build
   ```

2. **Deploy to Netlify/Vercel**:
   - Upload the `dist/spa` folder to your preferred static hosting service
   - Update the API base URL in the frontend to point to your Railway backend

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `RAILWAY_ENVIRONMENT` | Enables production mode | `production` |
| `DJANGO_SECRET_KEY` | Django secret key | Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | Django debug mode | `False` |
| `DATABASE_URL` | PostgreSQL connection | Automatically set by Railway |

### Post-Deployment Setup

1. **Create Superuser**:
   ```bash
   # In Railway console or locally with production DB
   python manage.py createsuperuser
   ```

2. **Load Sample Data** (optional):
   ```bash
   python create_sample_data.py
   ```

3. **Test the API**:
   - Visit `https://your-app-name.railway.app/api/docs/`
   - Test authentication and basic functionality

### Features Included in Deployment

✅ **Backend API** (Django REST Framework)
- Recipe management with PDF import
- Meal planning system
- Shopping list generation
- Family management with child users
- User authentication
- API documentation (Swagger)

✅ **Database** (PostgreSQL)
- All models and relationships
- Automatic migrations on deploy

✅ **Static Files** (WhiteNoise)
- Admin interface assets
- API documentation assets

✅ **Security**
- HTTPS enforcement
- CORS configuration
- Production security headers

### Troubleshooting

**Build Fails**:
- Check Railway logs for specific error messages
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

**Database Issues**:
- Ensure PostgreSQL service is running
- Check DATABASE_URL environment variable
- Run migrations manually if needed

**Static Files Not Loading**:
- Verify WhiteNoise is in MIDDLEWARE
- Check STATIC_ROOT and STATICFILES_DIRS settings
- Run `collectstatic` command

### Monitoring

- **Railway Dashboard**: Monitor deployments, logs, and metrics
- **Health Check**: Configured at `/api/docs/` endpoint
- **Logs**: Available in Railway console for debugging

### Scaling

Railway automatically handles:
- **Auto-scaling**: Based on traffic
- **Load balancing**: For high availability
- **Database backups**: Automatic PostgreSQL backups
- **SSL certificates**: Automatic HTTPS

### Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month for small apps
- **Pro Plan**: $20/month for production apps
- **Database**: Included in plans
- **Bandwidth**: Generous limits included

---

## 🎉 Your Recipe Meal Planner is now live!

Access your deployed application at: `https://your-app-name.railway.app`

### Next Steps:
1. Set up your family and invite members
2. Import your favorite recipes
3. Start planning meals together
4. Generate shopping lists
5. Enjoy organized meal planning! 🍽️