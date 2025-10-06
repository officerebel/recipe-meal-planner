#!/bin/bash

# Railway Volume Setup for Media Files
echo "🚀 Setting up Railway volume for media file persistence..."

# 1. Add volume to Railway project
echo "📁 Adding volume to Railway..."
railway volume create --name recipe-media --size 1GB

# 2. Mount volume to media directory
echo "🔗 Mounting volume to /app/media..."
railway volume attach recipe-media --mount-path /app/media

# 3. Update environment variables
echo "⚙️ Setting environment variables..."
railway variables set MEDIA_ROOT=/app/media
railway variables set MEDIA_URL=/media/

# 4. Redeploy with volume
echo "🚀 Redeploying with volume..."
railway up

echo "✅ Railway volume setup complete!"
echo "📝 Media files will now persist across deployments"