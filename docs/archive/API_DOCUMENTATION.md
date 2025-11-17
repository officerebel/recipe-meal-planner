# Recipe Meal Planner - API Documentation

## 🔗 API Overview

The Recipe Meal Planner API is built with Django REST Framework and provides comprehensive endpoints for recipe management, meal planning, and shopping list generation.

**Base URL**: `http://localhost:8000/api/`  
**Authentication**: Token-based authentication  
**Content Type**: `application/json`

## 🔐 Authentication

### Token Authentication
All API requests require authentication using a token in the Authorization header:

```http
Authorization: Token your-auth-token-here
```

### Authentication Endpoints

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

#### Register
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

## 🍳 Recipe Management API

### List Recipes
```http
GET /api/recipes/
```

**Query Parameters:**
- `search` - Search in title and description
- `categories` - Filter by categories (comma-separated)
- `tags` - Filter by tags (comma-separated)
- `page` - Page number for pagination
- `page_size` - Number of items per page

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/recipes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Spaghetti Carbonara",
      "description": "Classic Italian pasta dish",
      "prep_time": 15,
      "cook_time": 20,
      "total_time": 35,
      "servings": 4,
      "categories": ["Dinner", "Italian"],
      "tags": ["Quick", "Easy"],
      "ingredients": [
        {
          "name": "Spaghetti",
          "amount": "400g",
          "notes": "",
          "category": "pantry"
        }
      ],
      "instructions": [
        "Boil water for pasta",
        "Cook spaghetti according to package directions"
      ],
      "source": "manual",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

### Get Recipe Details
```http
GET /api/recipes/{id}/
```

### Create Recipe
```http
POST /api/recipes/
Content-Type: application/json

{
  "title": "New Recipe",
  "description": "Recipe description",
  "prep_time": 15,
  "cook_time": 30,
  "servings": 4,
  "categories": ["Dinner"],
  "tags": ["Healthy"],
  "ingredients": [
    {
      "name": "Chicken breast",
      "amount": "500g",
      "notes": "boneless, skinless",
      "category": "meat"
    }
  ],
  "instructions": [
    "Preheat oven to 200°C",
    "Season chicken with salt and pepper"
  ]
}
```

### Update Recipe
```http
PUT /api/recipes/{id}/
Content-Type: application/json
```

### Delete Recipe
```http
DELETE /api/recipes/{id}/
```

### Import Recipe from PDF
```http
POST /api/recipes/import-pdf/
Content-Type: multipart/form-data

{
  "file": [PDF file],
  "title": "Optional custom title"
}
```

## 📅 Meal Planning API

### List Meal Plans
```http
GET /api/meal-plans/
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Week 1 - January 2025",
      "start_date": "2025-01-06",
      "end_date": "2025-01-12",
      "total_days": 7,
      "total_meals": 15,
      "created_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

### Get Meal Plan Details
```http
GET /api/meal-plans/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Week 1 - January 2025",
  "start_date": "2025-01-06",
  "end_date": "2025-01-12",
  "total_days": 7,
  "total_meals": 15,
  "daily_meals": [
    {
      "date": "2025-01-06",
      "meal_assignments": [
        {
          "id": 1,
          "meal_type": "breakfast",
          "recipe": {
            "id": 5,
            "title": "Oatmeal with Berries"
          },
          "servings_planned": 2,
          "notes": ""
        }
      ]
    }
  ]
}
```

### Create Meal Plan
```http
POST /api/meal-plans/
Content-Type: application/json

{
  "name": "My Meal Plan",
  "start_date": "2025-01-13",
  "end_date": "2025-01-19"
}
```

### Assign Meal to Plan
```http
POST /api/meal-plans/{id}/assign-meal/
Content-Type: application/json

{
  "date": "2025-01-13",
  "meal_type": "breakfast",
  "recipe_id": 5,
  "servings_planned": 2,
  "notes": "Extra berries"
}
```

### Remove Meal Assignment
```http
DELETE /api/meal-assignments/{assignment_id}/
```

## 🛒 Shopping List API

### List Shopping Lists
```http
GET /api/shopping-lists/
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Week 1 Shopping",
      "start_date": "2025-01-06",
      "end_date": "2025-01-12",
      "total_items": 25,
      "purchased_items": 10,
      "created_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

### Get Shopping List Details
```http
GET /api/shopping-lists/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Week 1 Shopping",
  "start_date": "2025-01-06",
  "end_date": "2025-01-12",
  "total_items": 25,
  "purchased_items": 10,
  "items": [
    {
      "id": 1,
      "ingredient_name": "Chicken breast",
      "total_amount": "1000",
      "unit": "g",
      "category": "meat",
      "notes": "boneless, skinless",
      "purchased": false,
      "meal_types": ["lunch", "dinner"]
    }
  ],
  "meal_plans": [
    {
      "id": 1,
      "name": "Week 1 - January 2025"
    }
  ]
}
```

### Generate Shopping List
```http
POST /api/shopping-lists/generate/
Content-Type: application/json

{
  "name": "My Shopping List",
  "start_date": "2025-01-06",
  "end_date": "2025-01-12",
  "meal_plan_ids": [1, 2]
}
```

### Toggle Item Purchased Status
```http
PATCH /api/shopping-list-items/{item_id}/
Content-Type: application/json

{
  "purchased": true
}
```

### Add Custom Item to Shopping List
```http
POST /api/shopping-lists/{id}/add-item/
Content-Type: application/json

{
  "ingredient_name": "Milk",
  "total_amount": "1",
  "unit": "liter",
  "category": "dairy",
  "notes": "Organic"
}
```

## 📊 Categories and Tags API

### List Recipe Categories
```http
GET /api/recipes/categories/
```

### List Recipe Tags
```http
GET /api/recipes/tags/
```

### List Ingredient Categories
```http
GET /api/ingredients/categories/
```

## ⚠️ Error Handling

### Standard Error Response Format
```json
{
  "error": "Error message",
  "details": {
    "field_name": ["Field-specific error message"]
  },
  "code": "ERROR_CODE"
}
```

### Common HTTP Status Codes
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Authentication Errors
```json
{
  "error": "Authentication credentials were not provided.",
  "code": "AUTHENTICATION_REQUIRED"
}
```

### Validation Errors
```json
{
  "error": "Validation failed",
  "details": {
    "title": ["This field is required."],
    "servings": ["Ensure this value is greater than 0."]
  },
  "code": "VALIDATION_ERROR"
}
```

## 🔄 Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641024000
```

## 📝 API Versioning

The API uses URL versioning:
- Current version: `v1`
- Base URL: `/api/v1/`

Future versions will be available at `/api/v2/`, etc.

## 🧪 Testing the API

### Using cURL
```bash
# Get recipes
curl -H "Authorization: Token your-token" \
     http://localhost:8000/api/recipes/

# Create recipe
curl -X POST \
     -H "Authorization: Token your-token" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test Recipe","servings":4}' \
     http://localhost:8000/api/recipes/
```

### Using Postman
1. Set Authorization header: `Token your-token`
2. Set Content-Type: `application/json`
3. Use the endpoints documented above

### API Documentation Interface
Visit `http://localhost:8000/api/docs/` for interactive API documentation (Swagger UI).

---

**API Version**: 1.0  
**Last Updated**: January 2025  
**Support**: See project repository for issues and questions