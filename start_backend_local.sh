#!/bin/bash

echo "🚀 Starting Backend Server Locally"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "recipe_planner_env" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python -m venv recipe_planner_env"
    echo "   source recipe_planner_env/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source recipe_planner_env/bin/activate

# Check if requirements are installed
echo "🔍 Checking dependencies..."
python -c "import django" 2>/dev/null || {
    echo "❌ Django not found. Installing requirements..."
    pip install -r requirements.txt
}

# Change to backend directory
cd backend

# Set environment variables for local development
export DEBUG=True
export DATABASE_URL="sqlite:///db.sqlite3"
export SECRET_KEY="local-development-key-not-for-production"
export CORS_ALLOW_ALL_ORIGINS=True

echo "🔧 Running migrations..."
python manage.py migrate

echo "📊 Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Created admin user: admin/admin123')
else:
    print('✅ Admin user already exists')
"

echo "🌐 Starting Django development server..."
echo ""
echo "📋 Server Information:"
echo "   🔗 Backend API: http://localhost:8000"
echo "   🔗 Admin Panel: http://localhost:8000/admin/"
echo "   🔗 API Docs: http://localhost:8000/api/docs/"
echo "   👤 Admin Login: admin / admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver 0.0.0.0:8000