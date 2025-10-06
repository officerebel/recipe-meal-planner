# 📚 Recipe Meal Planner API Documentation

## 🚀 Quick Start

### Base URLs
- **Local Development**: `http://localhost:8000/api`
- **Production**: `https://proud-mercy-production.up.railway.app/api`

### Authentication
All endpoints (except health check and registration) require JWT authentication:
```
Authorization: Bearer <your-jwt-token>
```

## 📋 Postman Collection

Import the Postman collection: [`postman-collection.json`](./postman-collection.json)

### Collection Variables
- `base_url`: API base URL
- `auth_token`: JWT token (auto-populated after login)

## 🔐 Authentication Endpoints

### Register User
```http
POST /auth/register/
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "testpass123",
  "first_name": "Test",
  "last_name": "User"
}
```

### Login User
```http
POST /auth/login/
Content-Type: application/json

{
  "username": "demo_user",
  "password": "demo123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "demo_user",
    "email": "demo@example.com",
    "first_name": "Demo",
    "last_name": "User"
  }
}
```

## 🍳 Recipe Endpoints

### List Recipes
```http
GET /recipes/?scope=personal&search=pasta&category=Hoofdgerecht
```

**Query Parameters:**
- `scope`: `personal` | `family` (default: `personal`)
- `search`: Search in title, description, ingredients
- `category`: Filter by category
- `tag`: Filter by tag
- `source`: Filter by source (`pdf`, `manual`, `database`)

### Create Recipe
```http
POST /recipes/
Content-Type: application/json

{
  "title": "Spaghetti Carbonara",
  "description": "Classic Italian pasta dish",
  "prep_time": 15,
  "cook_time": 20,
  "servings": 4,
  "categories": ["Hoofdgerecht"],
  "tags": ["Snel", "Comfort Food"],
  "ingredients": [
    {
      "name": "Spaghetti",
      "amount": "400",
      "unit": "gram",
      "category": "pantry"
    }
  ],
  "instructions": [
    {
      "step_number": 1,
      "instruction": "Kook de spaghetti al dente"
    }
  ]
}
```

### Import Recipe from PDF
```http
POST /recipes/import_pdf/
Content-Type: multipart/form-data

file: [PDF file]
```

## 📅 Meal Planning Endpoints

### List Meal Plans
```http
GET /meal-plans/?scope=family
```

### Create Meal Plan
```http
POST /meal-plans/
Content-Type: application/json

{
  "name": "Week 1 Meal Plan",
  "start_date": "2024-01-08",
  "end_date": "2024-01-14",
  "servings": 4,
  "daily_meals": [
    {
      "date": "2024-01-08",
      "meal_assignments": [
        {
          "meal_type": "dinner",
          "recipe_id": "uuid-here",
          "servings_planned": 4
        }
      ]
    }
  ]
}
```

## 🛒 Shopping List Endpoints

### Generate Shopping List
```http
POST /shopping-lists/
Content-Type: application/json

{
  "name": "Weekly Shopping List",
  "meal_plan_ids": ["uuid-here"],
  "start_date": "2024-01-08",
  "end_date": "2024-01-14"
}
```

### Toggle Item Purchased
```http
PATCH /shopping-list-items/{item_id}/toggle_purchased/
Content-Type: application/json

{
  "purchased": true
}
```

## 👨‍👩‍👧‍👦 Family Management Endpoints

### Create Family
```http
POST /families/
Content-Type: application/json

{
  "name": "My Family",
  "description": "Our family meal planning",
  "default_servings": 4
}
```

### Create Family Member
```http
POST /families/create_member/
Content-Type: application/json

{
  "first_name": "New",
  "last_name": "Member",
  "email": "member@example.com",
  "username": "newmember",
  "password": "password123",
  "role": "member"
}
```

**Roles:**
- `admin`: Full family management access
- `member`: Can create/edit recipes and meal plans
- `child`: Simplified interface, view and suggest only
- `viewer`: Read-only access

### Update Family Member
```http
PATCH /families/{family_id}/update_member/
Content-Type: application/json

{
  "member_id": "uuid-here",
  "role": "admin",
  "first_name": "Updated",
  "last_name": "Name",
  "email": "updated@example.com"
}
```

## 📊 Utility Endpoints

### Health Check
```http
GET /health/
```

### API Schema (OpenAPI)
```http
GET /schema/
```

### Recipe Statistics
```http
GET /recipes/statistics/
```

## 🔄 Personal vs Family Scope

Most endpoints support a `scope` parameter:

- **`scope=personal`**: Returns only the current user's data
- **`scope=family`**: Returns data from all family members

This allows for:
- **Personal Recipe Collection**: User's own recipes
- **Family Recipe Sharing**: All family members' recipes
- **Personal Meal Plans**: Individual planning
- **Family Meal Coordination**: Shared family meal planning

## 📝 Response Formats

### Success Response
```json
{
  "id": "uuid-here",
  "title": "Recipe Title",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": {
    "field": ["Field-specific error"]
  }
}
```

### Paginated Response
```json
{
  "count": 25,
  "next": "http://api/recipes/?page=2",
  "previous": null,
  "results": [...]
}
```

## 🧪 Testing with Sample Data

The API includes sample data for testing:

**Demo User Credentials:**
- Username: `demo_user`
- Password: `demo123`

**Sample Recipes:**
- Spaghetti Carbonara
- Griekse Salade
- Pannenkoeken

## 🔒 Security Notes

- All passwords are hashed using Django's built-in password hashing
- JWT tokens expire after 24 hours
- CORS is configured for frontend domains
- Input validation prevents SQL injection and XSS attacks
- File uploads are validated for type and size

## 📱 Mobile API Considerations

- All endpoints are mobile-friendly
- Responses include optimized image URLs
- Pagination prevents large data transfers
- Offline-first design with proper caching headers