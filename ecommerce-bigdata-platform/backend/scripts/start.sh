#!/bin/bash

# E-commerce BigData Platform Backend Start Script

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Print current working directory
print_status "Current working directory: $(pwd)"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./scripts/bootstrap.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Please create one with your credentials"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Load environment variables
print_status "Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Check if required environment variables are set
if [ -z "$MONGODB_URL" ]; then
    print_warning "MONGODB_URL not set in .env"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    print_warning "JWT_SECRET_KEY not set in .env"
fi

# Start the server
print_status "Starting FastAPI server..."
print_success "Server will be available at: http://localhost:8000"
print_success "API Documentation: http://localhost:8000/docs"
echo ""

# Start uvicorn with reload for development
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 