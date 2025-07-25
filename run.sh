#!/bin/bash

# Interestify Run Script
# This script starts both the backend and frontend servers

set -e  # Exit on any error

echo "🚀 Starting Interestify Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to cleanup processes on exit
cleanup() {
    print_status "Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
    fi
    print_success "Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    print_error "run.sh must be run from the project root directory"
    exit 1
fi

# Check if build has been run
if [ ! -d ".venv" ]; then
    print_error "Python virtual environment not found. Please run './build.sh' first"
    exit 1
fi

if [ ! -d "client/node_modules" ]; then
    print_error "Node.js dependencies not found. Please run './build.sh' first"
    exit 1
fi

print_status "Starting Interestify v2.0..."

# Check environment file
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating basic configuration..."
    cp .env.example .env 2>/dev/null || cat > .env << EOF
DATABASE_URL=sqlite:///./interestify.db
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
DEFAULT_RATE_LIMIT=100
EOF
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment
source .venv/bin/activate

# Start backend server
print_status "Starting FastAPI backend server on http://localhost:8000..."

# Use --reload only if INTERESTIFY_ENV is not set to 'production'
if [ "$INTERESTIFY_ENV" = "production" ]; then
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
else
    python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
fi
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    print_error "Failed to start backend server. Check logs/backend.log for details"
    exit 1
fi

print_success "Backend server started (PID: $BACKEND_PID)"

# Start frontend server
print_status "Starting React frontend server on http://localhost:3000..."
cd client
npm run build > ../logs/frontend.log 2>&1

# Serve the production build with a simple HTTP server
npx serve -s build > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! ps -p $FRONTEND_PID > /dev/null; then
    print_error "Failed to start frontend server. Check logs/frontend.log for details"
    cleanup
    exit 1
fi

print_success "Frontend server started (PID: $FRONTEND_PID)"

print_success "🎉 Interestify is now running!"
print_status "Access the application at:"
echo "  📱 Frontend: http://localhost:3000"
echo "  🔧 API: http://localhost:8000"
echo "  📚 API Documentation: http://localhost:8000/docs"
echo ""
print_status "Logs are available in:"
echo "  📋 Backend: logs/backend.log"
echo "  📋 Frontend: logs/frontend.log"
echo ""
print_warning "Press Ctrl+C to stop all servers"

# Wait for user interruption
while true; do
    sleep 1
    # Check if processes are still running
    if ! ps -p $BACKEND_PID > /dev/null; then
        print_error "Backend server stopped unexpectedly"
        cleanup
        exit 1
    fi
    if ! ps -p $FRONTEND_PID > /dev/null; then
        print_error "Frontend server stopped unexpectedly"
        cleanup
        exit 1
    fi
done
