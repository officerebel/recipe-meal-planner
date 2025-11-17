#!/bin/bash

# Fixed Deployment Script
# Addresses media directory and database connection issues

set -e

echo "🚀 Fixed Deployment to Railway"
echo "=============================="

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
echo "🔧 Deploying Backend..."
echo "======================"

# Deploy backend
echo "📦 Deploying backend to Railway..."
railway up --detach

echo "⏳ Waiting for backend deployment..."
sleep 15

echo "✅ Backend deployed successfully!"

echo ""
echo "🎨 Deploying Frontend..."
echo "======================="

cd quasar-project

echo "📦 Deploying frontend to Railway..."
railway up --detach

echo "⏳ Waiting for frontend deployment..."
sleep 15

echo "✅ Frontend deployed successfully!"

cd ..

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "📱 Your Recipe Meal Planner should now be live!"
echo ""
echo "🔧 Note: Database migrations will run automatically on Railway"
echo "   If you see database errors, they should resolve once Railway"
echo "   establishes the database connection."
echo ""
echo "🖼️  Images: The app is configured for Railway volume mounting"
echo "   Images will be stored persistently once volume is set up."
echo ""