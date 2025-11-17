#!/bin/bash

# Simple deployment script focusing on image support

set -e

echo "🚀 Simple Deployment with Image Support"
echo "======================================"

# Deploy Backend
echo "🔧 Deploying Backend..."
railway up --detach

echo "⏳ Waiting for deployment..."
sleep 10

echo "🔄 Running migrations..."
railway run python manage.py migrate

echo "📊 Collecting static files..."
railway run python manage.py collectstatic --noinput

echo "✅ Backend deployed!"

# Deploy Frontend
echo "🎨 Deploying Frontend..."
cd quasar-project
railway up --detach
cd ..

echo "✅ Frontend deployed!"

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "🖼️  To test images:"
echo "   1. Go to your Railway frontend URL"
echo "   2. Create a recipe with an image"
echo "   3. Check if image displays correctly"
echo ""
echo "🔧 If images don't work:"
echo "   1. Check Railway logs for upload errors"
echo "   2. Verify image URLs in browser network tab"
echo "   3. Test direct image URL access"
echo ""