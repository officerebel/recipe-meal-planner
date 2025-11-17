#!/bin/bash

echo "🚀 Deploying frontend from frontend/ directory..."

# Navigate to frontend directory
cd frontend

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Make sure you're in the right directory."
    exit 1
fi

echo "📦 Found package.json, proceeding with deployment..."

# Connect to frontend project
railway link --project 969ad447-7cc3-4c24-aa2f-e93a7b9f625f --service mealplanner_frontend

# Deploy from current directory (frontend/)
railway up

echo "✅ Frontend deployment complete!"
echo "🌐 Check your app at: https://mealplannerfrontend-production.up.railway.app"