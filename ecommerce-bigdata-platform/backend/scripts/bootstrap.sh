#!/bin/bash

# E-commerce BigData Platform Backend Bootstrap Script
# This script sets up the complete backend environment

set -e  # Exit on any error

echo "🚀 E-commerce BigData Platform Backend Bootstrap"
echo "================================================"

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
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

# Step 1: Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    print_success "Python $python_version is compatible"
else
    print_error "Python 3.8+ is required. Found: $python_version"
    exit 1
fi

# Step 2: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Step 3: Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Step 4: Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Step 5: Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Dependencies installed"

# Step 6: Check environment file
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please update .env with your actual credentials"
    else
        print_error "No .env.example found. Please create .env file manually"
        exit 1
    fi
else
    print_success ".env file exists"
fi

# Step 7: Initialize database
print_status "Initializing database..."
python3 -c "
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from database import init_database
asyncio.run(init_database())
"
print_success "Database initialized"

# Step 8: Setup Kafka topics
print_status "Setting up Kafka topics..."
if [ -f "scripts/setup-kafka.sh" ]; then
    bash scripts/setup-kafka.sh
else
    print_warning "Kafka setup script not found. Please run manually:"
    print_warning "  cd ../cloud-services/kafka && ./setup.sh"
fi

# Step 9: Health check
print_status "Running health check..."
if [ -f "scripts/health-check.sh" ]; then
    bash scripts/health-check.sh
else
    print_warning "Health check script not found"
fi

echo ""
print_success "🎉 Bootstrap completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update .env with your actual credentials"
echo "2. Run: ./scripts/start.sh"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "Default admin credentials:"
echo "  Email: admin@ecommerce.com"
echo "  Password: admin123" 