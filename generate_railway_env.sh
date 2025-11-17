#!/bin/bash
# Generate Railway Environment Variables

echo "🚀 Railway Environment Variables Setup"
echo "========================================"
echo ""

# Generate SECRET_KEY
SECRET_KEY=$(openssl rand -base64 50 | tr -d '\n')
echo "SECRET_KEY (copy this to Railway):"
echo "$SECRET_KEY"
echo ""

# Instructions
echo "📋 Steps to fix Railway deployment:"
echo ""
echo "1. Add PostgreSQL Database:"
echo "   - In Railway dashboard: New → Database → Add PostgreSQL"
echo "   - This auto-sets DATABASE_URL"
echo ""
echo "2. Add Redis (recommended):"
echo "   - In Railway dashboard: New → Database → Add Redis"
echo "   - This auto-sets REDIS_URL"
echo ""
echo "3. Set Environment Variables in Railway:"
echo "   Variables tab → Add these:"
echo ""
echo "   SECRET_KEY=$SECRET_KEY"
echo ""
echo "   ALLOWED_HOSTS=.railway.app"
echo ""
echo "   CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app"
echo ""
echo "4. Redeploy:"
echo "   - Railway will auto-redeploy after adding database"
echo "   - Or manually trigger: Settings → Redeploy"
echo ""
echo "✅ After setup, your healthcheck should pass!"
