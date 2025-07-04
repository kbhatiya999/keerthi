#!/bin/bash

# E-commerce BigData Platform Kafka Setup Script

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

echo "📡 Setting up Kafka Topics for E-commerce Platform"
echo "=================================================="

# Check if confluent CLI is installed
if ! command -v confluent &> /dev/null; then
    print_error "Confluent CLI not found. Please install it first:"
    print_error "  curl -L --http1.1 https://cnfl.io/cli | sh -s -- -b /usr/local/bin"
    exit 1
fi

# Check if logged in to Confluent Cloud
if ! confluent kafka cluster list &> /dev/null; then
    print_error "Not logged in to Confluent Cloud. Please run:"
    print_error "  confluent login"
    exit 1
fi

# List of topics to create
TOPICS=(
    "ecommerce-user-events"
    "ecommerce-orders"
    "ecommerce-inventory"
    "ecommerce-clickstream"
    "ecommerce-payments"
)

print_status "Creating Kafka topics..."

for topic in "${TOPICS[@]}"; do
    print_status "Creating topic: $topic"
    if confluent kafka topic create "$topic" --partitions 3 --if-not-exists; then
        print_success "Topic '$topic' created successfully"
    else
        print_warning "Topic '$topic' might already exist or creation failed"
    fi
done

print_status "Listing all topics..."
confluent kafka topic list

print_success "🎉 Kafka topics setup completed!"
echo ""
echo "Topics created:"
for topic in "${TOPICS[@]}"; do
    echo "  - $topic"
done 