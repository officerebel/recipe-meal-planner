# Technical Design Document
## Recipe Meal Planner

**Version:** 1.1.0  
**Last Updated:** 2025-11-17  
**Status:** Living Document

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Database Design](#database-design)
4. [API Endpoints](#api-endpoints)
5. [Features](#features)
6. [Security](#security)
7. [Testing Strategy](#testing-strategy)
8. [Deployment](#deployment)

---

## System Overview

### Purpose
Recipe Meal Planner is a full-stack web application for managing recipes, planning meals, and generating shopping lists with family sharing capabilities.

### Key Features
- 📖 Recipe management with PDF import
- 📅 Meal planning (weekly/monthly)
- 🛒 Automatic shopping list generation
- 👨‍👩‍👧‍👦 Family sharing and collaboration
- 🔐 User authentication and authorization
- 📱 Mobile-responsive design

### Technology Stack

**Backend:**
- Django 5.2 (Python web framework)
- Django REST Framework 3.16 (API)
- PostgreSQL (Production database)
- SQLite (Development database)
- Gunicorn (WSGI server)

**Frontend:**
- Vue 3 (JavaScript framework)
- Quasar 2 (UI framework)
- Pinia (State management)
- Axios (HTTP client)

**Infrastructure:**
- Railway (Cloud platform)
- Docker (Containerization)
- GitHub (Version control)

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Vue 3 + Quasar (SPA)                            │  │
│  │  - Pages, Components, Stores                     │  │
│  │  - Axios HTTP Client                             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   API Gateway Layer                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Django REST Framework                           │  │
│  │  - Authentication, CORS, Rate Limiting           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Recipes  │  │   Meal   │  │ Families │  │  Auth  │ │
│  │   App    │  │ Planning │  │   App    │  │  App   │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  PostgreSQL  │  │   AWS S3     │  │    Redis     │ │
│  │  (Database)  │  │   (Media)    │  │   (Cache)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Application Structure

```
food_app/
├── backend/
│   ├── recipe_meal_planner/      # Django project
│   │   ├── settings.py           # Configuration
│   │   ├── config.py             # Config helpers
│   │   ├── urls.py               # URL routing
│   │   └── wsgi.py               # WSGI entry point
│   ├── recipes/                  # Recipe app
│   │   ├── models.py             # Recipe, Ingredient models
│   │   ├── views.py              # API views
│   │   ├── serializers.py        # DRF serializers
│   │   ├── services.py           # Business logic, PDF parsing
│   │   └── tests.py              # Unit tests
│   ├── meal_planning/            # Meal planning app
│   │   ├── models.py             # MealPlan, ShoppingList models
│   │   ├── views.py              # API views
│   │   ├── serializers.py        # DRF serializers
│   │   └── services.py           # Shopping list generation
│   ├── families/                 # Family management app
│   │   ├── models.py             # Family, FamilyMember models
│   │   ├── views.py              # API views
│   │   └── permissions.py        # Role-based permissions
│   └── authentication/           # Auth app
│       ├── views.py              # Login, register, password reset
│       └── serializers.py        # User serializers
├── frontend/
│   ├── src/
│   │   ├── pages/                # Vue pages
│   │   ├── components/           # Reusable components
│   │   ├── stores/               # Pinia stores
│   │   ├── boot/                 # Quasar boot files
│   │   └── router/               # Vue Router
│   ├── Dockerfile                # Frontend container
│   └── package.json              # Dependencies
└── docs/                         # Documentation
```

---

## Database Design

### Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│    User     │───────│ FamilyMember │───────│   Family    │
└─────────────┘  1:N  └──────────────┘  N:1  └─────────────┘
      │                                              │
      │ 1:N                                          │ 1:N
      ▼                                              ▼
┌─────────────┐                              ┌─────────────┐
│   Recipe    │                              │  MealPlan   │
└─────────────┘                              └─────────────┘
      │                                              │
      │ 1:N                                          │ 1:N
      ▼                                              ▼
┌─────────────┐                              ┌─────────────┐
│ Ingredient  │                              │MealAssignment│
└─────────────┘                              └─────────────┘
                                                    │
                                                    │ N:1
                                                    ▼
                                             ┌─────────────┐
                                             │ShoppingList │
                                             └─────────────┘
                                                    │
                                                    │ 1:N
                                                    ▼
                                             ┌─────────────┐
                                             │ShoppingList │
                                             │    Item     │
                                             └─────────────┘
```

### Core Models

#### User (Django Auth)
```python
- id: UUID (PK)
- username: String (unique)
- email: String (unique)
- password: String (hashed)
- first_name: String
- last_name: String
- is_active: Boolean
- date_joined: DateTime
```

#### Recipe
```python
- id: UUID (PK)
- user: FK(User)
- family: FK(Family, nullable)
- title: String
- description: Text
- prep_time: Integer (minutes)
- cook_time: Integer (minutes)
- servings: Integer
- instructions: JSONField (array)
- categories: JSONField (array)
- tags: JSONField (array)
- image: ImageField
- source: Enum (MANUAL, PDF, URL, API)
- is_shared: Boolean
- created_at: DateTime
- updated_at: DateTime
```

#### Ingredient
```python
- id: UUID (PK)
- recipe: FK(Recipe)
- name: String
- amount: String
- unit: String
- category: String
- notes: Text
```

#### Family
```python
- id: UUID (PK)
- name: String
- created_by: FK(User)
- created_at: DateTime
- updated_at: DateTime
```

#### FamilyMember
```python
- id: UUID (PK)
- family: FK(Family)
- user: FK(User)
- role: Enum (ADMIN, MEMBER, CHILD)
- joined_at: DateTime
```

#### MealPlan
```python
- id: UUID (PK)
- user: FK(User)
- family: FK(Family, nullable)
- name: String
- start_date: Date
- end_date: Date
- is_shared: Boolean
- created_at: DateTime
- updated_at: DateTime
```

#### MealAssignment
```python
- id: UUID (PK)
- meal_plan: FK(MealPlan)
- recipe: FK(Recipe)
- date: Date
- meal_type: Enum (BREAKFAST, LUNCH, DINNER, SNACK)
- servings: Integer
- notes: Text
```

#### ShoppingList
```python
- id: UUID (PK)
- user: FK(User)
- family: FK(Family, nullable)
- name: String
- start_date: Date
- end_date: Date
- is_shared: Boolean
- generated_at: DateTime
- meal_plans: M2M(MealPlan)
```

#### ShoppingListItem
```python
- id: UUID (PK)
- shopping_list: FK(ShoppingList)
- ingredient_name: String
- amount: String
- unit: String
- category: String
- purchased: Boolean
- purchased_at: DateTime
- notes: Text
```

### Database Indexes

```sql
-- Performance indexes
CREATE INDEX idx_recipe_user ON recipes_recipe(user_id);
CREATE INDEX idx_recipe_family ON recipes_recipe(family_id);
CREATE INDEX idx_recipe_created ON recipes_recipe(created_at);
CREATE INDEX idx_mealplan_dates ON meal_planning_mealplan(start_date, end_date);
CREATE INDEX idx_shoppinglist_user ON meal_planning_shoppinglist(user_id);
```

---

## API Endpoints

### Authentication

```
POST   /api/auth/register/          Register new user
POST   /api/auth/login/             Login user
POST   /api/auth/logout/            Logout user
POST   /api/auth/password-reset/    Request password reset
POST   /api/auth/password-reset-confirm/  Confirm password reset
GET    /api/auth/user/              Get current user
```

### Recipes

```
GET    /api/recipes/                List recipes
POST   /api/recipes/                Create recipe
GET    /api/recipes/{id}/           Get recipe details
PUT    /api/recipes/{id}/           Update recipe
PATCH  /api/recipes/{id}/           Partial update
DELETE /api/recipes/{id}/           Delete recipe
POST   /api/recipes/import_pdf/     Import from PDF
POST   /api/recipes/{id}/share/     Share with family
```

### Meal Planning

```
GET    /api/meal-plans/             List meal plans
POST   /api/meal-plans/             Create meal plan
GET    /api/meal-plans/{id}/        Get meal plan details
PUT    /api/meal-plans/{id}/        Update meal plan
DELETE /api/meal-plans/{id}/        Delete meal plan
POST   /api/meal-plans/{id}/assignments/  Add meal assignment
```

### Shopping Lists

```
GET    /api/shopping-lists/         List shopping lists
POST   /api/shopping-lists/generate/  Generate from meal plans
GET    /api/shopping-lists/{id}/    Get shopping list
DELETE /api/shopping-lists/{id}/    Delete shopping list
PATCH  /api/shopping-lists/{id}/items/{item_id}/  Mark item purchased
```

### Families

```
GET    /api/families/               List families
POST   /api/families/               Create family
GET    /api/families/{id}/          Get family details
PATCH  /api/families/{id}/          Update family
DELETE /api/families/{id}/          Delete family
POST   /api/families/{id}/invite/   Invite member
POST   /api/families/{id}/members/{member_id}/  Update member role
DELETE /api/families/{id}/members/{member_id}/  Remove member
```

---

## Features

### 1. Recipe Management

**Functional Requirements:**
- Users can create, read, update, delete recipes
- Recipes include title, description, ingredients, instructions
- Support for images, prep/cook time, servings
- Categorization with tags and categories
- Search and filter capabilities

**Technical Implementation:**
- Django models with UUID primary keys
- Image upload to S3 or local storage
- Full-text search on title and ingredients
- Pagination for large result sets

### 2. PDF Import

**Functional Requirements:**
- Import recipes from PDF files
- Extract title, ingredients, instructions, times
- Support Dutch and English recipes
- Handle various PDF formats

**Technical Implementation:**
- PyPDF2 for PDF text extraction
- Regex patterns for parsing
- Service layer (`recipes/services.py`)
- Comprehensive test suite (31 tests)

**See:** [PDF Parser Tests](../backend/recipes/TEST_README.md)

### 3. Meal Planning

**Functional Requirements:**
- Create weekly/monthly meal plans
- Assign recipes to specific dates and meal types
- View calendar-style meal plan
- Share meal plans with family

**Technical Implementation:**
- Date-based meal assignments
- Many-to-many relationship with recipes
- Family sharing with permissions
- Calendar view in frontend

### 4. Shopping List Generation

**Functional Requirements:**
- Generate shopping lists from meal plans
- Combine ingredients from multiple recipes
- Categorize items (produce, dairy, etc.)
- Mark items as purchased
- Share lists with family

**Technical Implementation:**
- Aggregation of ingredients
- Smart combining of similar items
- Category-based grouping
- Real-time updates via API

### 5. Family Sharing

**Functional Requirements:**
- Create family groups
- Invite members via email
- Role-based permissions (Admin, Member, Child)
- Share recipes, meal plans, shopping lists

**Technical Implementation:**
- Family model with members
- Role-based access control
- Email invitations
- Shared vs. personal content filtering

---

## Security

### Authentication
- JWT token-based authentication
- Token expiration and refresh
- Secure password hashing (Django default)

### Authorization
- Role-based access control (RBAC)
- Object-level permissions
- Family membership validation

### Data Protection
- HTTPS only in production
- CORS configuration
- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection (Vue escaping)

### Environment Variables
- Secrets in environment variables
- No hardcoded credentials
- `.env` files not in version control

**See:** [Environment Variables](ENVIRONMENT_VARIABLES.md)

---

## Testing Strategy

### Unit Tests
- Model tests
- Service layer tests
- PDF parser tests (31 tests)
- Serializer tests

### Integration Tests
- API endpoint tests
- Authentication flow tests
- Permission tests

### Test Coverage
- Target: 80%+ code coverage
- Critical paths: 100% coverage
- PDF parser: 100% coverage

**Run Tests:**
```bash
# All tests
python manage.py test

# Specific app
python manage.py test recipes

# With coverage
coverage run --source='.' manage.py test
coverage report
```

**See:** [PDF Parser Tests](../backend/recipes/TEST_README.md)

---

## Deployment

### Production Environment
- **Platform:** Railway
- **Backend:** Django + Gunicorn
- **Frontend:** Quasar + Serve
- **Database:** PostgreSQL
- **Storage:** AWS S3 (optional)

### CI/CD
- Git push triggers deployment
- Automatic builds on Railway
- Environment-specific configuration

### Monitoring
- Railway logs
- Health check endpoint (`/api/health/`)
- Error tracking (future: Sentry)

### Scaling
- Horizontal scaling via Railway
- Database connection pooling
- Static file CDN (future)

**See:** [12-Factor App](12_FACTOR_APP.md)

---

## Future Enhancements

### Phase 2: Backing Services
- [ ] Redis for caching
- [ ] Redis for session storage
- [ ] Connection pooling

### Phase 3: Background Jobs
- [ ] Celery for async tasks
- [ ] Email sending queue
- [ ] PDF processing queue

### Phase 4: Features
- [ ] Recipe recommendations
- [ ] Nutritional information
- [ ] Meal prep scheduling
- [ ] Mobile app (React Native)

---

*Last updated: 2025-11-17*
