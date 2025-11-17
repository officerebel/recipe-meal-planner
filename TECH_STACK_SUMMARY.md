# Tech Stack Summary - Recipe Meal Planner

## Frontend
- **Framework:** Quasar Framework v2 (Vue 3)
- **Language:** JavaScript
- **Build Tool:** Vite
- **State Management:** Pinia
- **HTTP Client:** Axios
- **UI Components:** Quasar Material Design
- **Deployment:** Railway (Static Site)
- **URL:** https://mealplannerfrontend-production.up.railway.app

## Backend
- **Framework:** Django 5.2.7
- **Language:** Python 3.12
- **API:** Django REST Framework 3.16.1
- **Database:** PostgreSQL (Railway)
- **Cache:** Local Memory (Redis optional)
- **Authentication:** Token-based (Django REST Framework)
- **File Storage:** Railway Volume (AWS S3 optional)
- **Server:** Gunicorn
- **Deployment:** Railway (Docker)
- **URL:** https://proud-mercy-production.up.railway.app

## Key Libraries

### Backend
- **PDF Processing:** PyPDF2 3.0.1, pdfplumber
- **Image Processing:** Pillow 11.0.0, opencv-python-headless 4.8.1.78
- **OCR:** pytesseract 0.3.10, easyocr 1.7.0
- **API Documentation:** drf-spectacular 0.28.0
- **CORS:** django-cors-headers 4.6.0
- **Database:** psycopg2-binary 2.9.9, dj-database-url 2.1.0
- **Static Files:** whitenoise 6.6.0
- **Cloud Storage:** django-storages 1.14.2, boto3 1.34.34
- **Cache:** django-redis 5.4.0, redis 5.0.1

### Frontend
- **Router:** Vue Router
- **HTTP:** Axios
- **State:** Pinia
- **UI:** Quasar Components

## Infrastructure

### Development
- **Local Backend:** http://localhost:8000
- **Local Frontend:** http://localhost:9000
- **Database:** SQLite (development)
- **Cache:** Local Memory

### Production (Railway)
- **Backend Service:** proud-mercy
- **Frontend Service:** mealplannerfrontend
- **Database:** PostgreSQL (Railway Plugin)
- **Storage:** Railway Volume (/app/media)
- **Cache:** Local Memory (Redis available but not configured)

## Architecture

```
┌─────────────────────────────────────────┐
│      Frontend (Quasar/Vue 3)           │
│   mealplannerfrontend-production       │
├─────────────────────────────────────────┤
│      REST API (Django REST Framework)   │
│         proud-mercy-production          │
├─────────────────────────────────────────┤
│        Business Logic Layer             │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │   Recipe    │  │   Meal Planning │   │
│  │   Service   │  │    Service      │   │
│  └─────────────┘  └─────────────────┘   │
├─────────────────────────────────────────┤
│         Data Access Layer               │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │   Django    │  │   Django        │   │
│  │   Models    │  │   Models        │   │
│  └─────────────┘  └─────────────────┘   │
├─────────────────────────────────────────┤
│   Storage Layer (PostgreSQL/Django ORM) │
└─────────────────────────────────────────┘
```

## Development Tools
- **Version Control:** Git + GitHub
- **Package Manager (Backend):** pip + requirements.txt
- **Package Manager (Frontend):** npm
- **Containerization:** Docker (Railway)
- **CI/CD:** Railway (GitHub integration)

## Environment Variables

### Backend (Production)
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - Django secret key
- `DEBUG` - False
- `ALLOWED_HOSTS` - Railway domains
- `CORS_ALLOWED_ORIGINS` - Frontend URL
- `RAILWAY_VOLUME_MOUNT_PATH` - /app/media

### Frontend (Production)
- `NODE_ENV` - production
- API calls to: https://proud-mercy-production.up.railway.app/api

## Key Features
- ✅ PDF Recipe Import with OCR
- ✅ Recipe Management (CRUD)
- ✅ Meal Planning Calendar
- ✅ Shopping List Generation
- ✅ Family Sharing
- ✅ Token Authentication
- ✅ Image Upload & Storage
- ✅ Responsive UI (Mobile & Desktop)

## Deployment Status
- ✅ Backend: Live on Railway
- ✅ Frontend: Live on Railway
- ✅ Database: PostgreSQL connected
- ✅ CORS: Configured
- ✅ Static Files: Served via WhiteNoise
- ✅ Media Files: Railway Volume

## Performance
- **Backend Response Time:** ~200-500ms
- **Frontend Load Time:** ~1-2s
- **PDF Processing:** ~5-10s per document
- **Database Queries:** Optimized with select_related/prefetch_related

## Security
- ✅ HTTPS enforced (Railway edge)
- ✅ CSRF protection enabled
- ✅ Token-based authentication
- ✅ CORS properly configured
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection (Django templates)

## Monitoring
- Railway deployment logs
- Django error logging
- Health check endpoint: `/api/health/`

## Future Improvements
- [ ] Add Redis for caching
- [ ] Implement AWS S3 for media storage
- [ ] Add Celery for background tasks
- [ ] Implement full-text search
- [ ] Add recipe recommendations
- [ ] Implement nutritional information
- [ ] Add recipe scaling
- [ ] Implement recipe sharing

---

**Last Updated:** November 17, 2025
**Version:** 1.0.0
