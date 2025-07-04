#!/bin/bash

# E-commerce BigData Platform Health Check Script

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🏥 E-commerce BigData Platform Health Check"
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local description=$2
    
    print_status "Checking $description..."
    if curl -s -f "$url" > /dev/null; then
        print_success "$description is healthy"
        return 0
    else
        print_error "$description is not responding"
        return 1
    fi
}

# Function to check Python module
check_python_module() {
    local module=$1
    local description=$2
    
    print_status "Checking $description..."
    if python3 -c "import $module" 2>/dev/null; then
        print_success "$description is available"
        return 0
    else
        print_error "$description is not available"
        return 1
    fi
}

# Initialize counters
total_checks=0
passed_checks=0

# Check 1: Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ "$python_version" == 3.* ]]; then
    print_success "Python $python_version is compatible"
    ((passed_checks++))
else
    print_error "Python 3.x is required. Found: $python_version"
fi
((total_checks++))

# Check 2: Required Python packages
print_status "Checking Python dependencies..."
REQUIRED_PACKAGES=("fastapi" "uvicorn" "motor" "pymongo" "python-jose" "passlib" "confluent_kafka")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if check_python_module "$package" "$package"; then
        ((passed_checks++))
    fi
    ((total_checks++))
done

# Check 3: Environment variables
print_status "Checking environment variables..."
REQUIRED_ENV_VARS=("MONGODB_URL" "JWT_SECRET_KEY")
for var in "${REQUIRED_ENV_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        print_success "$var is set"
        ((passed_checks++))
    else
        print_warning "$var is not set"
    fi
    ((total_checks++))
done

# Check 4: MongoDB connection
print_status "Checking MongoDB connection..."
if python3 -c "
import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_mongo():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGODB_URL'))
        await client.admin.command('ping')
        print('MongoDB connection successful')
        return True
    except Exception as e:
        print(f'MongoDB connection failed: {e}')
        return False

asyncio.run(test_mongo())
" 2>/dev/null; then
    print_success "MongoDB connection is healthy"
    ((passed_checks++))
else
    print_error "MongoDB connection failed"
fi
((total_checks++))

# Check 5: Kafka connection (if confluent CLI is available)
if command_exists confluent; then
    print_status "Checking Kafka connection..."
    if confluent kafka cluster list &>/dev/null; then
        print_success "Kafka connection is healthy"
        ((passed_checks++))
    else
        print_warning "Kafka connection failed (not logged in)"
    fi
    ((total_checks++))
else
    print_warning "Confluent CLI not found, skipping Kafka check"
fi

# Check 6: API health (if server is running)
print_status "Checking API health..."
if check_http "http://localhost:8000/health" "API server"; then
    ((passed_checks++))
else
    print_warning "API server is not running (start with: ./scripts/start.sh)"
fi
((total_checks++))

# Summary
echo ""
echo "📊 Health Check Summary"
echo "======================"
echo "Total checks: $total_checks"
echo "Passed: $passed_checks"
echo "Failed: $((total_checks - passed_checks))"

if [ $passed_checks -eq $total_checks ]; then
    print_success "🎉 All health checks passed!"
    exit 0
else
    print_warning "⚠️  Some health checks failed. Please review the issues above."
    exit 1
fi 