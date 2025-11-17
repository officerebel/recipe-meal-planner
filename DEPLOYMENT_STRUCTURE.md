# Deployment Structure

## Current Setup

### Backend Service (Django)
- **Location**: Root directory
- **Dockerfile**: `Dockerfile` (root)
- **Railway Config**: `railway.json` (root)
- **Working Directory**: `/app/backend` (inside container)
- **Start Command**: `start.sh` or Dockerfile CMD

**Deployment:**
```bash
# From root directory
railway up
```

### Frontend Service (Quasar)
- **Location**: `frontend/` directory
- **Dockerfile**: `frontend/Dockerfile`
- **Railway Config**: `frontend/railway.json`
- **Working Directory**: `/app` (inside container)
- **Start Command**: `serve dist/spa -s -l $PORT`

**Deployment:**
```bash
# From frontend directory
cd frontend
railway up
```

## How It Works

### Backend Deployment Flow
1. Railway reads `railway.json` in root
2. Builds using `Dockerfile` in root
3. Dockerfile copies everything to `/app`
4. Changes working directory to `/app/backend`
5. Runs migrations and collectstatic
6. Starts Gunicorn

### Frontend Deployment Flow
1. Railway reads `frontend/railway.json`
2. Builds using `frontend/Dockerfile`
3. Dockerfile builds Quasar app
4. Serves static files with `serve`

## File Structure

```
food_app/
├── Dockerfile                 ← Backend Docker config
├── railway.json               ← Backend Railway config
├── start.sh                   ← Backend start script
├── requirements.txt           ← Python dependencies
├── backend/                   ← Django code
│   ├── recipe_meal_planner/
│   ├── recipes/
│   ├── meal_planning/
│   ├── families/
│   ├── authentication/
│   └── manage.py
└── frontend/                  ← Quasar code
    ├── Dockerfile             ← Frontend Docker config
    ├── railway.json           ← Frontend Railway config
    ├── start.sh               ← Frontend start script
    └── package.json           ← Node dependencies
```

## Railway Services

### Service 1: Backend (proud-mercy-production)
- **URL**: https://proud-mercy-production.up.railway.app
- **Root Directory**: `/` (project root)
- **Build**: Uses root `Dockerfile`
- **Environment Variables**:
  - `DATABASE_URL` (auto-set by Railway)
  - `SECRET_KEY`
  - `ALLOWED_HOSTS`
  - `CORS_ALLOWED_ORIGINS`

### Service 2: Frontend (mealplannerfrontend-production)
- **URL**: https://mealplannerfrontend-production.up.railway.app
- **Root Directory**: `frontend/`
- **Build**: Uses `frontend/Dockerfile`
- **Environment Variables**:
  - `VITE_API_BASE_URL=https://proud-mercy-production.up.railway.app`
  - `PORT` (auto-set by Railway)

## Deployment Commands

### Deploy Backend Only
```bash
# From project root
railway up
```

### Deploy Frontend Only
```bash
# From project root
cd frontend
railway up
```

### Deploy Both
```bash
# Terminal 1: Backend
railway up

# Terminal 2: Frontend
cd frontend
railway up
```

## Health Checks

### Backend
- **Endpoint**: `/api/health/`
- **Expected**: `{"status": "healthy", "service": "recipe-meal-planner"}`

### Frontend
- **Endpoint**: `/`
- **Expected**: HTML page with Quasar app

## Troubleshooting

### Backend Issues
```bash
# Check logs
railway logs --service backend

# Check if backend is in correct directory
railway run bash
cd backend
ls -la
```

### Frontend Issues
```bash
# Check logs
railway logs --service frontend

# Verify build output
railway run bash
ls -la dist/spa
```

## Why This Structure Works

1. **Separation of Concerns**: Backend and frontend are independent
2. **Railway Compatibility**: Each service has its own config
3. **Docker Optimization**: Each service has optimized Dockerfile
4. **Easy Development**: Can deploy services independently
5. **Clean Structure**: All Django code in `backend/`, all Vue code in `frontend/`

## Migration Notes

After restructuring (moving Django to `backend/`):
- ✅ Dockerfile already uses `/app/backend` as working directory
- ✅ `start.sh` already changes to `backend/` directory
- ✅ No changes needed to Railway configuration
- ✅ Deployment continues to work as before

The restructure was **deployment-safe** because:
1. Dockerfile copies everything to `/app` (includes `backend/` folder)
2. Then changes working directory to `/app/backend`
3. All Django commands run from correct location
