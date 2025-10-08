#!/bin/bash

echo "🚀 Setting up Railway backend with roles and admin user..."
echo "=================================================="

# Connect to backend project
echo "📡 Connecting to backend project..."
railway link --project db23d37f-1cd3-4d1a-a8dd-a7bece1abc30 --service proud-mercy

# Deploy the updated code with the setup command
echo "📦 Deploying updated backend code..."
cd backend
railway up --detach

echo "⏳ Waiting for deployment to complete..."
sleep 30

# Run the setup command
echo "🔧 Running initial data setup..."
railway run python manage.py setup_initial_data --username admin --email admin@example.com --password admin123 --family-name "My Family"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🌐 Your applications:"
echo "   Frontend: https://mealplannerfrontend-production.up.railway.app"
echo "   Backend:  https://proud-mercy-production.up.railway.app"
echo "   API Docs: https://proud-mercy-production.up.railway.app/api/docs/"
echo ""
echo "🔐 Login with:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "✅ You should now see roles in your settings page!"