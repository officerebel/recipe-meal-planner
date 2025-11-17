#!/bin/bash

# Railway Deployment Script for Recipe & Meal Planner
# This script helps prepare and deploy your application to Railway

set -e  # Exit on any error

echo "🚀 Recipe & Meal Planner - Railway Deployment Helper"
echo "=================================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway..."
    railway login
fi

echo "✅ Railway CLI ready"

# Function to deploy backend
deploy_backend() {
    echo "🔧 Deploying Backend Service..."
    
    # Navigate to backend directory
    cd backend
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo "❌ requirements.txt not found in backend directory"
        exit 1
    fi
    
    # Deploy backend
    echo "📦 Deploying backend to Railway..."
    railway up
    
    # Get the backend URL
    BACKEND_URL=$(railway domain)
    echo "✅ Backend deployed to: $BACKEND_URL"
    
    cd ..
    return 0
}

# Function to deploy frontend
deploy_frontend() {
    echo "🎨 Deploying Frontend Service..."
    
    # Navigate to frontend directory
    cd frontend
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo "❌ package.json not found in frontend directory"
        exit 1
    fi
    
    # Update environment variables if backend URL is provided
    if [ ! -z "$1" ]; then
        echo "🔧 Updating frontend environment variables..."
        echo "VITE_API_BASE_URL=$1" > .env.production.local
    fi
    
    # Deploy frontend
    echo "📦 Deploying frontend to Railway..."
    railway up
    
    # Get the frontend URL
    FRONTEND_URL=$(railway domain)
    echo "✅ Frontend deployed to: $FRONTEND_URL"
    
    cd ..
    return 0
}

# Function to setup environment variables
setup_env_vars() {
    echo "🔧 Setting up environment variables..."
    
    # Backend environment variables
    echo "Setting backend environment variables..."
    cd backend
    
    # Generate a new secret key if not provided
    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    fi
    
    railway variables set SECRET_KEY="$SECRET_KEY"
    railway variables set DEBUG=False
    railway variables set ALLOWED_HOSTS=".railway.app"
    
    cd ..
    
    echo "✅ Environment variables configured"
}

# Main deployment flow
main() {
    echo "Starting deployment process..."
    
    # Check if this is a new project or existing
    read -p "Is this a new Railway project? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🆕 Creating new Railway project..."
        railway init
    fi
    
    # Setup environment variables
    setup_env_vars
    
    # Deploy backend first
    deploy_backend
    BACKEND_URL=$(cd backend && railway domain)
    
    # Deploy frontend with backend URL
    deploy_frontend "$BACKEND_URL"
    FRONTEND_URL=$(cd frontend && railway domain)
    
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================"
    echo "Backend URL:  $BACKEND_URL"
    echo "Frontend URL: $FRONTEND_URL"
    echo ""
    echo "📝 Next steps:"
    echo "1. Update CORS settings in Django with your frontend URL"
    echo "2. Create a superuser: railway run python manage.py createsuperuser"
    echo "3. Test your application at the frontend URL"
    echo ""
    echo "📚 For detailed instructions, see DEPLOYMENT.md"
}

# Run main function
main "$@"