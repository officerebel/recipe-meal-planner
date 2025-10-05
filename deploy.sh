#!/bin/bash

# Recipe Meal Planner - Railway Deployment Script
# This script helps deploy both backend and frontend to Railway

set -e

echo "🚀 Recipe Meal Planner - Railway Deployment"
echo "==========================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway first:"
    railway login
fi

echo ""
echo "📋 Deployment Options:"
echo "1. Deploy Backend (Django)"
echo "2. Deploy Frontend (Quasar)"
echo "3. Deploy Both"
echo "4. Update Frontend with Backend URL"
echo ""

read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo "🔧 Deploying Backend..."
        deploy_backend
        ;;
    2)
        echo "🎨 Deploying Frontend..."
        deploy_frontend
        ;;
    3)
        echo "🚀 Deploying Both Services..."
        deploy_backend
        deploy_frontend
        ;;
    4)
        echo "🔗 Updating Frontend Configuration..."
        update_frontend_config
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

deploy_backend() {
    echo ""
    echo "🔧 Deploying Django Backend..."
    echo "==============================="
    
    # Check if we're in the right directory
    if [ ! -f "manage.py" ]; then
        echo "❌ manage.py not found. Make sure you're in the project root directory."
        exit 1
    fi
    
    # Deploy backend
    echo "📦 Creating Railway service for backend..."
    railway up --detach
    
    echo ""
    echo "✅ Backend deployment initiated!"
    echo "📝 Don't forget to:"
    echo "   1. Add PostgreSQL database in Railway dashboard"
    echo "   2. Set environment variables (SECRET_KEY, EMAIL settings)"
    echo "   3. Run migrations: railway shell -> python manage.py migrate"
    echo ""
    
    # Get the backend URL
    BACKEND_URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "")
    if [ ! -z "$BACKEND_URL" ]; then
        echo "🌐 Backend URL: $BACKEND_URL"
        echo "📋 Save this URL for frontend configuration!"
    fi
}

deploy_frontend() {
    echo ""
    echo "🎨 Deploying Quasar Frontend..."
    echo "==============================="
    
    # Navigate to frontend directory
    if [ ! -d "quasar-project" ]; then
        echo "❌ quasar-project directory not found."
        exit 1
    fi
    
    cd quasar-project
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo "❌ package.json not found in quasar-project directory."
        exit 1
    fi
    
    # Deploy frontend
    echo "📦 Creating Railway service for frontend..."
    railway up --detach
    
    echo ""
    echo "✅ Frontend deployment initiated!"
    echo "📝 Don't forget to update CORS settings in backend with frontend URL"
    
    # Get the frontend URL
    FRONTEND_URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "")
    if [ ! -z "$FRONTEND_URL" ]; then
        echo "🌐 Frontend URL: $FRONTEND_URL"
    fi
    
    cd ..
}

update_frontend_config() {
    echo ""
    echo "🔗 Updating Frontend Configuration..."
    echo "===================================="
    
    read -p "Enter your backend Railway URL (e.g., https://backend-production.up.railway.app): " backend_url
    
    if [ -z "$backend_url" ]; then
        echo "❌ Backend URL is required"
        exit 1
    fi
    
    # Update axios configuration
    AXIOS_FILE="quasar-project/src/boot/axios.js"
    
    if [ ! -f "$AXIOS_FILE" ]; then
        echo "❌ Axios configuration file not found: $AXIOS_FILE"
        exit 1
    fi
    
    # Create backup
    cp "$AXIOS_FILE" "$AXIOS_FILE.backup"
    
    # Update the baseURL
    sed -i.tmp "s|https://proud-mercy-production.up.railway.app/api|${backend_url}/api|g" "$AXIOS_FILE"
    rm "$AXIOS_FILE.tmp" 2>/dev/null || true
    
    echo "✅ Updated frontend configuration with backend URL: ${backend_url}/api"
    echo "📝 Please commit and redeploy the frontend for changes to take effect"
}

echo ""
echo "🎉 Deployment script completed!"
echo ""
echo "📚 For detailed instructions, see RAILWAY_DEPLOYMENT.md"
echo "🔧 For troubleshooting, check Railway dashboard logs"
echo ""