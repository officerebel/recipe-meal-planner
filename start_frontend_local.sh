#!/bin/bash

echo "🚀 Starting Frontend Server Locally"
echo "==================================="

# Change to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Set environment variables for local development
export NODE_ENV=development

# Create local environment file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "🔧 Creating local environment configuration..."
    cat > .env.local << EOF
# Local development environment
VUE_APP_API_BASE_URL=http://localhost:8000/api
VUE_APP_BACKEND_URL=http://localhost:8000
QUASAR_API_BASE_URL=http://localhost:8000/api
EOF
    echo "✅ Created .env.local file"
fi

echo "🌐 Starting Quasar development server..."
echo ""
echo "📋 Server Information:"
echo "   🔗 Frontend: http://localhost:9000"
echo "   🔗 Backend API: http://localhost:8000/api"
echo ""
echo "Make sure the backend server is running on port 8000!"
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev