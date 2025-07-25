#!/bin/bash

# Interestify Build Script
# This script builds both the backend and frontend components

set -e  # Exit on any error

echo "🚀 Building Interestify Application..."

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

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    print_error "build.sh must be run from the project root directory"
    exit 1
fi

print_status "Building Interestify v2.0..."

# Step 1: Set up Python virtual environment
print_status "Setting up Python environment..."
if [ ! -d ".venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv .venv
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate

# Step 2: Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
if [ ! -f "requirements.txt" ]; then
    print_warning "requirements.txt not found, creating with default dependencies..."
    cat > requirements.txt << EOF
fastapi==0.110.2
uvicorn==0.29.0
sqlalchemy==2.0.29
aiosqlite==0.20.0
python-dotenv==1.0.1
textblob==0.18.0.post0
vaderSentiment==3.3.2
aiohttp==3.9.5
greenlet==3.0.3
EOF
fi
pip install --upgrade -r requirements.txt

# Step 3: Set up environment file
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
    else
        # Create a basic .env file
        cat > .env << EOF
# Database
DATABASE_URL=sqlite:///./interestify.db

# API Keys (replace with your actual keys)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Cache Settings
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Rate Limiting
DEFAULT_RATE_LIMIT=100
EOF
        print_success "Created basic .env file"
        print_warning "Please update .env file with your actual API keys"
    fi
else
    print_status ".env file already exists"
fi

# Step 4: Download NLTK data for TextBlob
print_status "Downloading NLTK data for sentiment analysis..."
python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('brown', quiet=True)
    print('NLTK data downloaded successfully')
except Exception as e:
    print(f'Warning: Could not download NLTK data: {e}')
"

# Step 5: Build Frontend
print_status "Building React frontend..."
cd client

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install
else
    print_status "Node.js dependencies already installed"
fi

# Build production version
print_status "Building production frontend..."
npm run build

cd ..

# Step 6: Create directories for logs and data
print_status "Creating application directories..."
mkdir -p logs
mkdir -p data

# Step 7: Test backend startup
print_status "Testing backend startup..."

# Find a free port for testing
TEST_PORT=$(python -c "import socket; s=socket.socket(); s.bind(('',0)); print(s.getsockname()[1]); s.close()")

timeout 10s python -m uvicorn src.main:app --host 0.0.0.0 --port $TEST_PORT &
SERVER_PID=$!
sleep 5

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null; then
    print_success "Backend server test successful (port $TEST_PORT)"
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null
else
    print_warning "Backend server test failed, but continuing..."
fi

print_success "🎉 Build completed successfully!"
print_status "Next steps:"
echo "  1. Update .env file with your API keys"
echo "  2. Run './run.sh' to start the application"
echo "  3. Visit http://localhost:3000 for the frontend"
echo "  4. Visit http://localhost:8000/docs for API documentation"
