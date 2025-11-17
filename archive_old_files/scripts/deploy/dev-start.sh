#!/bin/bash

# Recipe Meal Planner Development Startup Script

echo "🍳 Starting Recipe Meal Planner Development Environment"
echo "======================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists dotnet; then
    echo "❌ .NET SDK not found. Please install .NET 9.0 SDK"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Start backend in background
echo "🚀 Starting ASP.NET Core API..."
cd RecipeMealPlanner.Api
dotnet run &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Vue.js + Quasar frontend..."
cd recipe-meal-planner
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Development environment started!"
echo "📡 Backend API: https://localhost:5001"
echo "🌐 Frontend App: http://localhost:9000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Development environment stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for user to stop
wait