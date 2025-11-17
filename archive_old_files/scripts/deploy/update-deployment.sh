#!/bin/bash

# Update Railway Deployment Script
# This script updates both frontend and backend with latest changes

set -e

echo "🚀 Updating Railway Deployment"
echo "=============================="

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
    exit 1
fi

echo ""
echo "📋 What would you like to update?"
echo "1. Update Backend Only"
echo "2. Update Frontend Only" 
echo "3. Update Both (Recommended)"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo "🔧 Updating Backend..."
        update_backend
        ;;
    2)
        echo "🎨 Updating Frontend..."
        update_frontend
        ;;
    3)
        echo "🚀 Updating Both Services..."
        update_backend
        update_frontend
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

update_backend() {
    echo ""
    echo "🔧 Updating Django Backend..."
    echo "============================="
    
    # Check if we're in the right directory
    if [ ! -f "manage.py" ]; then
        echo "❌ manage.py not found. Make sure you're in the project root directory."
        exit 1
    fi
    
    echo "📦 Deploying backend updates..."
    railway up --detach
    
    echo "🔄 Running migrations..."
    railway run python manage.py migrate
    
    echo "📊 Collecting static files..."
    railway run python manage.py collectstatic --noinput
    
    echo "✅ Backend updated successfully!"
}

update_frontend() {
    echo ""
    echo "🎨 Updating Quasar Frontend..."
    echo "=============================="
    
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
    
    echo "📦 Deploying frontend updates..."
    railway up --detach
    
    echo "✅ Frontend updated successfully!"
    
    cd ..
}

echo ""
echo "🎉 Deployment update completed!"
echo ""
echo "📱 To see changes on your iPhone:"
echo "   1. Clear browser cache (Settings > Safari > Clear History and Website Data)"
echo "   2. Force refresh the page (pull down to refresh)"
echo "   3. Or try opening in private/incognito mode"
echo ""
echo "🔗 Your Railway URLs:"
echo "   Frontend: Check Railway dashboard for your frontend URL"
echo "   Backend: Check Railway dashboard for your backend URL"
echo ""