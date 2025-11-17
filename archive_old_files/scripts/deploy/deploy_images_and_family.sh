#!/bin/bash

echo "🚀 Deploying Images & Family Management Features..."

# 1. Set up Railway volume for images
echo "📁 Setting up Railway volume for persistent image storage..."
railway volume create --name recipe-media --size 2GB || echo "Volume may already exist"
railway volume attach recipe-media --mount-path /app/media || echo "Volume may already be attached"

# 2. Update environment variables
echo "⚙️ Setting environment variables..."
railway variables set MEDIA_ROOT=/app/media
railway variables set MEDIA_URL=/media/
railway variables set MAX_IMAGE_SIZE=5242880  # 5MB
railway variables set ALLOWED_IMAGE_EXTENSIONS=".jpg,.jpeg,.png,.gif,.webp"

# 3. Install image processing dependencies
echo "📦 Installing image processing dependencies..."
echo "Pillow==10.1.0" >> requirements.txt
echo "pillow-heif==0.13.0" >> requirements.txt

# 4. Run Django migrations for any model changes
echo "🔄 Running Django migrations..."
python manage.py makemigrations
python manage.py migrate

# 5. Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# 6. Deploy backend to Railway
echo "🚀 Deploying backend to Railway..."
railway up

# 7. Build and deploy frontend
echo "🎨 Building frontend..."
cd quasar-project
npm install
npm run build

echo "✅ Deployment complete!"
echo ""
echo "🎯 New Features Deployed:"
echo "  📸 Image Upload & Storage"
echo "  👥 Enhanced Family Management"
echo "  📱 Mobile-Optimized Interface"
echo "  🎛️ Family Dashboard"
echo "  ⚙️ Advanced Settings"
echo ""
echo "🔗 Next Steps:"
echo "  1. Deploy frontend build to your hosting service"
echo "  2. Test image uploads in production"
echo "  3. Verify family management features"
echo "  4. Set up family invitations (email service)"

cd ..