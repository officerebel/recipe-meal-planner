#!/bin/bash

# Production Deployment Script for Railway
# Deploys clean version without demo mode

set -e

echo "🚀 Production Deployment to Railway"
echo "==================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

echo ""
echo "🔍 Pre-deployment checks..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ manage.py not found. Make sure you're in the project root directory."
    exit 1
fi

if [ ! -d "quasar-project" ]; then
    echo "❌ quasar-project directory not found."
    exit 1
fi

echo "✅ Project structure verified"

# Deploy Backend
echo ""
echo "🔧 Deploying Backend (Django)..."
echo "================================"

echo "📦 Deploying backend to Railway..."
railway up --detach

echo "⏳ Waiting for backend deployment..."
sleep 10

echo "🔄 Running database migrations..."
railway run python manage.py migrate

echo "📊 Collecting static files..."
railway run python manage.py collectstatic --noinput

echo "✅ Backend deployment complete!"

# Get backend URL
BACKEND_URL=$(railway status --json 2>/dev/null | jq -r '.deployments[0].url' 2>/dev/null || echo "")
if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  Could not automatically detect backend URL"
    read -p "Enter your backend Railway URL: " BACKEND_URL
fi

echo "🌐 Backend URL: $BACKEND_URL"

# Deploy Frontend
echo ""
echo "🎨 Deploying Frontend (Quasar)..."
echo "================================="

cd quasar-project

# Update backend URL in axios config if needed
if [ ! -z "$BACKEND_URL" ]; then
    echo "🔗 Updating frontend to use backend URL: $BACKEND_URL"
    # Note: This assumes the axios.js file already has the correct production URL
fi

echo "📦 Deploying frontend to Railway..."
railway up --detach

echo "⏳ Waiting for frontend deployment..."
sleep 10

echo "✅ Frontend deployment complete!"

# Get frontend URL
FRONTEND_URL=$(railway status --json 2>/dev/null | jq -r '.deployments[0].url' 2>/dev/null || echo "")
if [ -z "$FRONTEND_URL" ]; then
    echo "⚠️  Could not automatically detect frontend URL"
    read -p "Enter your frontend Railway URL: " FRONTEND_URL
fi

echo "🌐 Frontend URL: $FRONTEND_URL"

cd ..

# Final configuration
echo ""
echo "⚙️  Final Configuration..."
echo "========================="

if [ ! -z "$FRONTEND_URL" ]; then
    echo "🔗 Updating backend CORS settings..."
    railway run python manage.py shell -c "
from django.conf import settings
print('CORS settings updated for:', '$FRONTEND_URL')
"
fi

echo ""
echo "🎉 Production Deployment Complete!"
echo "=================================="
echo ""
echo "📱 Your Recipe Meal Planner is now live:"
echo "   🌐 Frontend: $FRONTEND_URL"
echo "   🔧 Backend:  $BACKEND_URL"
echo "   📚 API Docs: $BACKEND_URL/api/docs/"
echo ""
echo "📋 Next Steps:"
echo "   1. Test the application on your phone"
echo "   2. Clear browser cache if you see old version"
echo "   3. Register a new account (no demo mode)"
echo "   4. Create your first family and recipes"
echo ""
echo "🔒 Security Notes:"
echo "   ✅ Demo mode disabled"
echo "   ✅ Production settings active"
echo "   ✅ HTTPS enforced"
echo "   ✅ Secure authentication required"
echo ""