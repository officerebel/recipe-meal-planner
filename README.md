# Recipe Meal Planner - Backend

Django REST API for the Recipe Meal Planner application.

## 🏗️ Architecture

- **Django 5.2** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Database
- **JWT Authentication** - User authentication
- **PDF Processing** - Recipe import from PDFs

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

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test recipes
python manage.py test meal_planning
python manage.py test families

# Run with coverage
coverage run --source='.' manage.py test
coverage report
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