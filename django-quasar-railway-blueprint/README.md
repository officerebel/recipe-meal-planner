# Django + Quasar Railway Blueprint

A production-ready template for deploying Django REST API + Quasar (Vue.js) frontend to Railway.

## 🚀 Quick Start

1. **Clone this repository**
   ```bash
   git clone <your-repo-url>
   cd django-quasar-railway-blueprint
   ```

2. **Deploy to Railway**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Access your app**
   - Backend API: `https://your-backend.railway.app/api/`
   - Frontend: `https://your-frontend.railway.app/`

## 📁 Project Structure

```
django-quasar-railway-blueprint/
├── backend/                 # Django REST API
│   ├── core/               # Django project settings
│   ├── api/                # API app
│   ├── requirements.txt    # Python dependencies
│   ├── railway.json        # Railway backend config
│   └── manage.py
├── frontend/               # Quasar (Vue.js) app
│   ├── src/               # Vue components and pages
│   ├── package.json       # Node.js dependencies
│   ├── quasar.config.js   # Quasar configuration
│   └── railway.json       # Railway frontend config
├── docs/                  # Documentation
└── scripts/               # Deployment scripts
```

## 🛠️ Features

### Backend (Django)
- ✅ Django REST Framework
- ✅ CORS configuration
- ✅ PostgreSQL database support
- ✅ Environment variables
- ✅ Static file serving
- ✅ Health check endpoint
- ✅ API documentation (Swagger)

### Frontend (Quasar/Vue)
- ✅ Quasar Framework (Vue 3)
- ✅ Vue Router
- ✅ Pinia state management
- ✅ Axios HTTP client
- ✅ Responsive design
- ✅ Production build optimization

### Deployment
- ✅ Railway configuration
- ✅ Environment-specific settings
- ✅ Automatic deployments
- ✅ Database migrations
- ✅ Static file handling

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app
```

**Frontend (.env)**
```env
VITE_API_BASE_URL=https://your-backend.railway.app/api
```

## 📚 Documentation

- [Backend Setup](./docs/backend-setup.md)
- [Frontend Setup](./docs/frontend-setup.md)
- [Railway Deployment](./docs/railway-deployment.md)
- [Environment Configuration](./docs/environment-config.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the Railway community**