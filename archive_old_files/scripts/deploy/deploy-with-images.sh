#!/bin/bash

# Production Deployment with Image Support
# Ensures Railway volume is properly configured for image uploads

set -e

echo "🚀 Deploying Recipe Meal Planner with Image Support"
echo "=================================================="

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

echo "✅ Project structure verified"

# Deploy Backend with Volume Support
echo ""
echo "🔧 Deploying Backend with Image Support..."
echo "========================================="

# Set Railway environment variables for production
echo "⚙️  Setting environment variables..."
railway variables --set RAILWAY_ENVIRONMENT=production
railway variables --set DEBUG=False
railway variables --set MEDIA_ROOT=/app/media
railway variables --set MEDIA_URL=/media/

# Create volume for persistent image storage
echo "💾 Setting up persistent volume for images..."
railway volume add --mount-path /app/media || echo "Volume may already exist"

echo "📦 Deploying backend to Railway..."
railway up --detach

echo "⏳ Waiting for backend deployment..."
sleep 15

echo "🔄 Running database migrations..."
railway run python manage.py migrate

echo "📊 Collecting static files..."
railway run python manage.py collectstatic --noinput

echo "🖼️  Testing image directory..."
railway run python -c "
import os
media_dir = '/app/media'
os.makedirs(media_dir, exist_ok=True)
print(f'Media directory exists: {os.path.exists(media_dir)}')
print(f'Media directory writable: {os.access(media_dir, os.W_OK)}')
print(f'Media directory contents: {os.listdir(media_dir) if os.path.exists(media_dir) else \"Not found\"}')
"

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
echo "🎨 Deploying Frontend..."
echo "======================="

cd quasar-project

# Update production environment file
echo "🔗 Updating frontend configuration..."
cat > .env.production << EOF
# Production Environment Configuration
VUE_APP_API_BASE_URL=$BACKEND_URL
VUE_APP_ENVIRONMENT=production
EOF

echo "📦 Building and deploying frontend..."
railway up --detach

echo "⏳ Waiting for frontend deployment..."
sleep 15

echo "✅ Frontend deployment complete!"

# Get frontend URL
FRONTEND_URL=$(railway status --json 2>/dev/null | jq -r '.deployments[0].url' 2>/dev/null || echo "")
if [ -z "$FRONTEND_URL" ]; then
    echo "⚠️  Could not automatically detect frontend URL"
    read -p "Enter your frontend Railway URL: " FRONTEND_URL
fi

echo "🌐 Frontend URL: $FRONTEND_URL"

cd ..

# Update CORS settings
echo ""
echo "⚙️  Updating CORS settings..."
echo "============================"

if [ ! -z "$FRONTEND_URL" ]; then
    railway variables --set CORS_ALLOWED_ORIGINS="$FRONTEND_URL"
    echo "🔗 CORS updated for: $FRONTEND_URL"
fi

# Test image upload functionality
echo ""
echo "🧪 Testing Image Upload..."
echo "========================="

railway run python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_meal_planner.settings')
django.setup()

from django.conf import settings
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
print(f'MEDIA_URL: {settings.MEDIA_URL}')
print(f'Media directory exists: {os.path.exists(settings.MEDIA_ROOT)}')

# Test write permissions
test_file = os.path.join(settings.MEDIA_ROOT, 'test.txt')
try:
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print('✅ Media directory is writable')
except Exception as e:
    print(f'❌ Media directory write test failed: {e}')
"

echo ""
echo "🎉 Deployment Complete with Image Support!"
echo "=========================================="
echo ""
echo "📱 Your Recipe Meal Planner is now live:"
echo "   🌐 Frontend: $FRONTEND_URL"
echo "   🔧 Backend:  $BACKEND_URL"
echo "   📚 API Docs: $BACKEND_URL/api/docs/"
echo "   🖼️  Images:   $BACKEND_URL/media/"
echo ""
echo "🖼️  Image Upload Testing:"
echo "   1. Go to: $FRONTEND_URL"
echo "   2. Create a recipe with an image"
echo "   3. Check if image displays correctly"
echo "   4. Image URLs should be: $BACKEND_URL/media/recipe_images/..."
echo ""
echo "🔧 Troubleshooting Images:"
echo "   - Check Railway volume is mounted at /app/media"
echo "   - Verify MEDIA_URL and MEDIA_ROOT settings"
echo "   - Test direct image URL access"
echo ""