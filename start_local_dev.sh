#!/bin/bash

echo "🚀 Starting Full Local Development Environment"
echo "=============================================="
echo ""
echo "This will start both backend and frontend servers."
echo "You'll need two terminal windows/tabs."
echo ""

# Make scripts executable
chmod +x start_backend_local.sh
chmod +x start_frontend_local.sh

echo "📋 Instructions:"
echo ""
echo "1️⃣  In Terminal 1 - Start Backend:"
echo "   ./start_backend_local.sh"
echo ""
echo "2️⃣  In Terminal 2 - Start Frontend:"
echo "   ./start_frontend_local.sh"
echo ""
echo "🌐 Once both are running, you can access:"
echo "   • Frontend: http://localhost:9000"
echo "   • Backend API: http://localhost:8000/api"
echo "   • Admin Panel: http://localhost:8000/admin/"
echo "   • API Docs: http://localhost:8000/api/docs/"
echo ""
echo "👤 Login credentials: admin / admin123"
echo ""
echo "🔧 To test duplicate removal:"
echo "   1. Create a shopping list with duplicates"
echo "   2. Use the API endpoint: POST /api/shopping-lists/{id}/remove-duplicates/"
echo ""

read -p "Press Enter to start backend server in this terminal..."

# Start backend server
./start_backend_local.sh