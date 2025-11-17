# Development Setup Guide

Get the Django + Quasar blueprint running locally for development.

## 🛠️ Prerequisites

- Python 3.9+ 
- Node.js 16+
- Git

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd django-quasar-railway-blueprint
```

### 2. Backend Setup (Django)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

### 3. Frontend Setup (Quasar)

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:9000`

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env` file:
```env
DEBUG=True
SECRET_KEY=your-development-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:9000,http://127.0.0.1:9000
```

### Frontend Environment Variables

The frontend automatically uses `http://localhost:8000/api` for development.

To override, set in `frontend/.env`:
```env
API_BASE_URL=http://localhost:8000/api
```

## 📁 Project Structure

```
django-quasar-railway-blueprint/
├── backend/                 # Django REST API
│   ├── core/               # Django project settings
│   │   ├── settings.py     # Main settings
│   │   ├── urls.py         # URL routing
│   │   └── wsgi.py         # WSGI config
│   ├── api/                # API application
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   ├── serializers.py  # DRF serializers
│   │   └── urls.py         # API URLs
│   ├── requirements.txt    # Python dependencies
│   └── manage.py           # Django management
├── frontend/               # Quasar application
│   ├── src/               # Source code
│   │   ├── components/    # Vue components
│   │   ├── pages/         # Page components
│   │   ├── layouts/       # Layout components
│   │   ├── stores/        # Pinia stores
│   │   └── boot/          # Boot files
│   ├── package.json       # Node dependencies
│   └── quasar.config.js   # Quasar configuration
└── docs/                  # Documentation
```

## 🧪 Development Workflow

### Backend Development

1. **Models**: Define in `backend/api/models.py`
2. **Serializers**: Create in `backend/api/serializers.py`
3. **Views**: Implement in `backend/api/views.py`
4. **URLs**: Add routes in `backend/api/urls.py`
5. **Migrations**: Run `python manage.py makemigrations && python manage.py migrate`

### Frontend Development

1. **Components**: Create in `frontend/src/components/`
2. **Pages**: Add in `frontend/src/pages/`
3. **Routes**: Configure in `frontend/src/router/routes.js`
4. **State**: Manage with Pinia stores in `frontend/src/stores/`
5. **API**: Use axios in boot file for API calls

## 🔍 API Documentation

With the development server running, visit:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🎨 Code Formatting

### Backend (Python)
```bash
cd backend
pip install black isort flake8
black .
isort .
flake8 .
```

### Frontend (JavaScript/Vue)
```bash
cd frontend
npm run lint
npm run format
```

## 🐛 Debugging

### Backend Debugging
- Use Django Debug Toolbar (install separately)
- Add `print()` statements or `import pdb; pdb.set_trace()`
- Check Django logs in terminal

### Frontend Debugging
- Use Vue DevTools browser extension
- Check browser console for errors
- Use `console.log()` for debugging

## 📦 Adding Dependencies

### Backend
```bash
cd backend
pip install package-name
pip freeze > requirements.txt
```

### Frontend
```bash
cd frontend
npm install package-name
# Dependencies automatically saved to package.json
```

## 🔄 Database Management

### Reset Database
```bash
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Backup Database
```bash
cd backend
python manage.py dumpdata > backup.json
```

### Restore Database
```bash
cd backend
python manage.py loaddata backup.json
```

## 🚀 Production Build

### Test Production Build Locally

Backend:
```bash
cd backend
DEBUG=False python manage.py runserver
```

Frontend:
```bash
cd frontend
npm run build
npx serve dist/spa -s -l 3000
```

## 🆘 Common Issues

1. **CORS Errors**: Check `CORS_ALLOWED_ORIGINS` in Django settings
2. **Module Not Found**: Ensure virtual environment is activated
3. **Port Already in Use**: Change port or kill existing process
4. **Database Locked**: Close any database connections
5. **Node Modules**: Delete `node_modules` and run `npm install`

## 📚 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Quasar Documentation](https://quasar.dev/)
- [Vue.js Guide](https://vuejs.org/guide/)
- [Pinia Documentation](https://pinia.vuejs.org/)