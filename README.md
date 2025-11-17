# Recipe Meal Planner

Full-stack meal planning application with recipe management, PDF import, family sharing, and shopping list generation.

## 🏗️ Architecture

**Backend:**
- **Django 5.2** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Production database
- **JWT Authentication** - User authentication
- **PDF Processing** - Recipe import from PDFs

**Frontend:**
- **Vue 3** - JavaScript framework
- **Quasar 2** - UI component framework
- **Pinia** - State management
- **Axios** - HTTP client

**Deployment:**
- **Railway** - Cloud platform (backend + frontend)
- **Docker** - Containerization
- **GitHub Actions** - CI/CD (future)

## 📁 Apps Structure

### `recipes/`
- Recipe CRUD operations
- PDF import functionality
- Image handling
- Categories and tags management

### `meal_planning/`
- Meal plan creation and management
- Shopping list generation
- Meal assignments

### `families/`
- Family group management
- Role-based permissions
- Member invitations

### `authentication/`
- User registration and login
- JWT token management
- Password reset

## 🚀 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_sample_data
```

### 4. Run Development Server
```bash
python manage.py runserver
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### Recipes
- `GET /api/recipes/` - List recipes
- `POST /api/recipes/` - Create recipe
- `GET /api/recipes/{id}/` - Get recipe details
- `PUT /api/recipes/{id}/` - Update recipe
- `DELETE /api/recipes/{id}/` - Delete recipe
- `POST /api/recipes/import_pdf/` - Import from PDF

### Meal Planning
- `GET /api/meal-plans/` - List meal plans
- `POST /api/meal-plans/` - Create meal plan
- `GET /api/shopping-lists/` - List shopping lists
- `POST /api/shopping-lists/generate/` - Generate shopping list

### Families
- `GET /api/families/` - List families
- `POST /api/families/` - Create family
- `POST /api/families/{id}/invite_member/` - Invite member
- `PATCH /api/families/{id}/update_member/` - Update member

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test recipes
python manage.py test meal_planning
python manage.py test families

# Run PDF parser tests
python manage.py test recipes.test_pdf_parser

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

**See also:** [PDF Parser Test Documentation](recipes/TEST_README.md)

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🔧 Management Commands

```bash
# Create sample data
python manage.py create_sample_data

# Clear cache
python manage.py clear_cache

# Export data
python manage.py dumpdata > backup.json
```

## 📈 Performance

- Database query optimization with `select_related` and `prefetch_related`
- Caching with Redis (production)
- Image optimization and compression
- API pagination for large datasets

## 🔒 Security

- CORS configuration for frontend
- JWT token authentication
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## 📚 Documentation

- **[PDF Parser Tests](recipes/TEST_README.md)** - Test suite for PDF recipe parsing
- **[12-Factor App](docs/12_FACTOR_APP.md)** - Implementation of 12-factor methodology
- **[API Documentation](http://localhost:8000/api/schema/swagger-ui/)** - Interactive API docs (when running)

## 🎯 12-Factor App Compliance

This application follows the [12-Factor App](https://12factor.net) methodology for building scalable, maintainable applications.

**Current Status:**
- ✅ Codebase - Single repo, multiple deploys
- ✅ Dependencies - Explicitly declared
- ⚠️ Config - Partially in environment variables
- ✅ Backing Services - Attached resources
- ✅ Build/Release/Run - Separate stages
- ⚠️ Processes - Mostly stateless
- ✅ Port Binding - Self-contained services
- ⚠️ Concurrency - Basic implementation
- ✅ Disposability - Fast startup/shutdown
- ⚠️ Dev/Prod Parity - Moderate similarity
- ⚠️ Logs - Stdout, needs structure
- ⚠️ Admin Processes - Basic management commands

**See:** [12-Factor App Implementation Guide](docs/12_FACTOR_APP.md) for detailed status and improvement roadmap.

## 🚢 Deployment

### Railway (Production)
```bash
# Backend
railway up

# Frontend
cd frontend
railway up
```

### Docker (Local)
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🛠️ Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes and test**
   ```bash
   python manage.py test
   cd frontend && npm run test
   ```

3. **Commit and push**
   ```bash
   git add .
   git commit -m "Add your feature"
   git push origin feature/your-feature
   ```

4. **Deploy to Railway**
   ```bash
   railway up  # Automatic on push to main
   ```

## 🐛 Debugging

### Backend Logs
```bash
# Local
python manage.py runserver --verbosity 2

# Production (Railway)
railway logs --service backend
```

### Frontend Logs
```bash
# Local
cd frontend
npm run dev

# Production (Railway)
railway logs --service frontend
```

### Common Issues

**Issue: PDF import returns "Imported Recipe"**
- Check logs for title extraction
- See [PDF Parser Tests](recipes/TEST_README.md) for debugging guide

**Issue: Frontend can't connect to backend**
- Check VITE_API_BASE_URL environment variable
- Verify CORS settings in backend

**Issue: Database connection error**
- Check DATABASE_URL environment variable
- Verify PostgreSQL is running

## 📦 Project Structure

```
food_app/
├── backend/
│   ├── recipe_meal_planner/    # Django project settings
│   ├── recipes/                # Recipe app
│   │   ├── test_pdf_parser.py  # PDF parser tests
│   │   └── TEST_README.md      # Test documentation
│   ├── meal_planning/          # Meal planning app
│   ├── families/               # Family management app
│   ├── authentication/         # Auth app
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/             # Vue pages
│   │   ├── components/        # Vue components
│   │   ├── stores/            # Pinia stores
│   │   └── boot/              # Quasar boot files
│   ├── package.json           # Node dependencies
│   └── Dockerfile             # Frontend container
├── docs/
│   └── 12_FACTOR_APP.md       # 12-factor documentation
└── README.md                  # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is private and proprietary.