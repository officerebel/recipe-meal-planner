# 🚀 Starting Local Development Servers

## Step 1: Start Backend Server

**Terminal 1:**
```bash
# Make sure you're in the project root directory
cd /Users/timvogt/Documents/food_app

# Start the backend server
./start_backend_local.sh
```

This will:
- ✅ Activate the virtual environment
- ✅ Run Django migrations
- ✅ Create admin user (admin/admin123)
- ✅ Start server on http://localhost:8000

## Step 2: Start Frontend Server

**Terminal 2 (new terminal window/tab):**
```bash
# Make sure you're in the project root directory
cd /Users/timvogt/Documents/food_app

# Start the frontend server
./start_frontend_local.sh
```

This will:
- ✅ Install frontend dependencies (if needed)
- ✅ Create local environment config
- ✅ Start Quasar dev server (usually on http://localhost:9000)

## 🌐 Access Points

Once both servers are running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend App** | http://localhost:9000 | Main application |
| **Backend API** | http://localhost:8000/api | REST API |
| **Admin Panel** | http://localhost:8000/admin | Django admin |
| **API Docs** | http://localhost:8000/api/docs | Swagger documentation |

## 👤 Login Credentials

- **Username:** admin
- **Password:** admin123

## 🔧 Testing Duplicate Removal

1. Create a shopping list with duplicate items
2. Use the API endpoint: `POST /api/shopping-lists/{id}/remove-duplicates/`
3. Or test with the demo script: `python demo_duplicates.py`

## ❗ Troubleshooting

If port 9000 doesn't work, the frontend might be running on a different port. Check the terminal output when starting the frontend server - it will show the actual URL.

Common Quasar dev server ports:
- http://localhost:9000 (default)
- http://localhost:8080 (alternative)
- http://localhost:3000 (alternative)