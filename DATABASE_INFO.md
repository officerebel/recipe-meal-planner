# Database Configuration Information

## Current Setup (as of November 13, 2025)

### Local Development Database
- **Type**: SQLite
- **Location**: `backend/db.sqlite3`
- **Contains**: Your original recipes and user data
- **Users**: demo@example.com, admin@example.com, and others

### Production Database (Railway)
- **Type**: PostgreSQL
- **Service**: Postgres-8HRU on Railway
- **Project**: meal-planner
- **Environment**: production
- **URL**: Available via `DATABASE_URL` environment variable
- **Connection**: `postgresql://postgres:WvMHyFtBjeRhqSgsGosF...@postgres-8hru.railway.internal:5432/railway`

### Backend Services
- **Local**: http://localhost:8000
- **Production**: https://proud-mercy-production.up.railway.app
- **Service Name**: proud-mercy

### Frontend Services  
- **Local**: http://localhost:9000
- **Production**: https://mealplannerfrontend-production.up.railway.app
- **Project**: mealplanner_frontend

## Database Migration Status

### Issue Identified
The production database (PostgreSQL) is currently empty or missing your recipes because:
1. Local development uses SQLite with your existing data
2. Production uses PostgreSQL which was recently set up
3. Data migration from SQLite to PostgreSQL hasn't been completed

### Solution Required
To restore your recipes to production:
1. Export data from local SQLite database
2. Import data to production PostgreSQL database
3. Ensure user accounts and recipes are properly migrated

## Authentication Issues Fixed
- ✅ Password change functionality working
- ✅ Logout functionality working  
- 🔄 Password reset functionality added (needs testing)

## Railway Project Structure
```
meal-planner (Backend)
├── proud-mercy (Django Backend Service)
└── Postgres-8HRU (PostgreSQL Database)

mealplanner_frontend (Frontend)
└── mealplanner_frontend (Quasar Frontend Service)
```

## Environment Variables (Production)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Django secret key
- `DEBUG`: False
- `CORS_ALLOWED_ORIGINS`: Frontend URL
- `VITE_API_BASE_URL`: Backend URL (in frontend)

## Next Steps
1. Test password reset functionality
2. Export local SQLite data
3. Import data to production PostgreSQL
4. Verify all recipes and users are available in production