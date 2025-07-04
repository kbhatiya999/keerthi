#!/bin/bash

echo "🗄️ MongoDB Atlas Setup"
echo "======================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    print_error "Environment file not found: $ENV_FILE"
    exit 1
fi

print_status "Loading environment variables from $ENV_FILE"
source "$ENV_FILE"

# MongoDB Atlas Configuration from environment
if [ -z "$MONGODB_URL" ] || [ -z "$MONGODB_DATABASE" ]; then
    print_error "MongoDB configuration missing from environment file"
    print_error "Please ensure MONGODB_URL and MONGODB_DATABASE are set in $ENV_FILE"
    exit 1
fi

DATABASE_NAME="$MONGODB_DATABASE"

print_status "Testing MongoDB Atlas connection..."
if mongosh "$MONGODB_URL" --eval "db.runCommand('ping')" --quiet > /dev/null 2>&1; then
    print_success "MongoDB Atlas connection successful"
else
    print_error "MongoDB Atlas connection failed"
    print_warning "Please check your credentials and network connection"
    exit 1
fi

# Create database and collections
print_status "Setting up database and collections..."

mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
// Create collections if they don't exist
db.createCollection('products');
db.createCollection('customers');
db.createCollection('orders');
db.createCollection('events');

// Create indexes for better performance
db.products.createIndex({ 'name': 1 });
db.products.createIndex({ 'price': 1 });
db.products.createIndex({ 'category': 1 });
db.orders.createIndex({ 'customer_id': 1 });
db.orders.createIndex({ 'created_at': -1 });
db.orders.createIndex({ 'status': 1 });
db.events.createIndex({ 'event_type': 1 });
db.events.createIndex({ 'customer_id': 1 });
db.events.createIndex({ 'timestamp': -1 });
db.customers.createIndex({ 'email': 1 });
db.customers.createIndex({ 'customer_id': 1 });

print('Database and collections setup complete');
" --quiet

if [ $? -eq 0 ]; then
    print_success "Database and collections created successfully"
else
    print_error "Failed to create database and collections"
    exit 1
fi

echo ""
print_success "🎉 MongoDB Atlas setup complete!"
echo ""
echo "📋 Next steps:"
echo "  - Run tests: ./cloud-services/mongodb/test-cli.sh"
echo "  - Connect: mongosh \"$MONGODB_URL\""
echo "  - GUI: Download MongoDB Compass from https://www.mongodb.com/try/download/compass"
echo ""
echo "📝 Note: Sample data creation is handled separately in the test script" 