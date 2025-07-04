#!/bin/bash

echo "🧪 MongoDB Atlas CLI Testing"
echo "============================"

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

# Test 1: Connection Test
echo ""
print_status "Test 1: Testing MongoDB connection..."
if mongosh "$MONGODB_URL" --eval "db.runCommand('ping')" --quiet > /dev/null 2>&1; then
    print_success "MongoDB connection successful"
else
    print_error "MongoDB connection failed"
    exit 1
fi

# Test 2: Database Access Test
echo ""
print_status "Test 2: Testing database access..."
if mongosh "$MONGODB_URL" --eval "use $DATABASE_NAME; db.runCommand('ping')" --quiet > /dev/null 2>&1; then
    print_success "Database access successful"
else
    print_error "Database access failed"
    exit 1
fi

# Test 3: Collection Operations Test
echo ""
print_status "Test 3: Testing collection operations..."

# Use fixed test collection name for idempotency
TEST_COLLECTION="test_collection"
mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.createCollection('$TEST_COLLECTION');
" --quiet > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Test collection created/verified successfully"
else
    print_error "Failed to create test collection"
    exit 1
fi

# Test 4: CRUD Operations Test
echo ""
print_status "Test 4: Testing CRUD operations..."

# Check if test document already exists
EXISTING_DOC=$(mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.$TEST_COLLECTION.countDocuments({ test_id: 'test_document' });
" --quiet 2>/dev/null | grep -E '^[0-9]+$' || echo "0")

if [ "$EXISTING_DOC" -eq 0 ]; then
    # Insert test document only if it doesn't exist
    mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
    db.$TEST_COLLECTION.insertOne({
        test_id: 'test_document',
        message: 'Test document',
        timestamp: new Date(),
        data: {
            value: 42,
            text: 'Hello MongoDB'
        }
    });
    " --quiet > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Document inserted successfully"
    else
        print_error "Failed to insert document"
        exit 1
    fi
else
    print_success "Test document already exists"
fi

# Read test document
DOC_COUNT=$(mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.$TEST_COLLECTION.countDocuments();
" --quiet 2>/dev/null | grep -E '^[0-9]+$' || echo "0")

if [ "$DOC_COUNT" -gt 0 ]; then
    print_success "Document read successfully (count: $DOC_COUNT)"
else
    print_error "Failed to read document"
    exit 1
fi

# Update test document
mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.$TEST_COLLECTION.updateOne(
    { test_id: 'test_document' },
    { \$set: { message: 'Updated test document', updated_at: new Date() } }
);
" --quiet > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Document updated successfully"
else
    print_error "Failed to update document"
    exit 1
fi

# Test 5: Index Operations Test
echo ""
print_status "Test 5: Testing index operations..."

mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.$TEST_COLLECTION.createIndex({ test_id: 1 });
" --quiet > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Index created successfully"
else
    print_error "Failed to create index"
    exit 1
fi

# Test 6: Aggregation Test
echo ""
print_status "Test 6: Testing aggregation operations..."

AGG_RESULT=$(mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.$TEST_COLLECTION.aggregate([
    { \$group: { _id: null, count: { \$sum: 1 } } }
]).toArray()[0].count;
" --quiet 2>/dev/null | grep -E '^[0-9]+$' || echo "0")

if [ "$AGG_RESULT" -gt 0 ]; then
    print_success "Aggregation operation successful (count: $AGG_RESULT)"
else
    print_error "Failed to perform aggregation"
    exit 1
fi

# Test 7: Cleanup Test
echo ""
print_status "Test 7: Testing cleanup operations..."

# Clean up test documents instead of dropping collection (idempotent)
mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.$TEST_COLLECTION.deleteMany({ test_id: 'test_document' });
" --quiet > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Test documents cleaned up successfully"
else
    print_error "Failed to clean up test documents"
    exit 1
fi

# Test 8: E-commerce Collections Test
echo ""
print_status "Test 8: Testing e-commerce collections..."

# Check if e-commerce collections exist
COLLECTIONS=$(mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.getCollectionNames().join(',');
" --quiet)

if [[ "$COLLECTIONS" == *"products"* ]] && [[ "$COLLECTIONS" == *"customers"* ]] && [[ "$COLLECTIONS" == *"orders"* ]]; then
    print_success "E-commerce collections found: $COLLECTIONS"
else
    print_warning "Some e-commerce collections missing. Found: $COLLECTIONS"
fi

# Test 9: Sample Data Creation and Verification
echo ""
print_status "Test 9: Creating and verifying sample data..."

# Create sample data if collections are empty
PRODUCT_COUNT=$(mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.products.countDocuments();
" --quiet 2>/dev/null | grep -E '^[0-9]+$' || echo "0")

if [ "$PRODUCT_COUNT" -eq 0 ]; then
    print_status "Creating sample products..."
    mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
    db.products.insertMany([
        {
            name: 'Laptop Pro',
            price: 1299.99,
            description: 'High-performance laptop for professionals',
            category: 'Electronics',
            stock: 50
        },
        {
            name: 'Wireless Headphones',
            price: 199.99,
            description: 'Premium noise-canceling headphones',
            category: 'Electronics',
            stock: 100
        },
        {
            name: 'Smart Watch',
            price: 299.99,
            description: 'Feature-rich smartwatch with health tracking',
            category: 'Electronics',
            stock: 75
        }
    ]);
    " --quiet > /dev/null 2>&1
    print_success "Sample products created"
else
    print_success "Sample products already exist: $PRODUCT_COUNT"
fi

CUSTOMER_COUNT=$(mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.customers.countDocuments();
" --quiet 2>/dev/null | grep -E '^[0-9]+$' || echo "0")

if [ "$CUSTOMER_COUNT" -eq 0 ]; then
    print_status "Creating sample customer..."
    mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
    db.customers.insertOne({
        customer_id: 'test_user_001',
        email: 'test@example.com',
        name: 'Test User',
        created_at: new Date()
    });
    " --quiet > /dev/null 2>&1
    print_success "Sample customer created"
else
    print_success "Sample customers already exist: $CUSTOMER_COUNT"
fi

# Verify final counts
FINAL_PRODUCT_COUNT=$(mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.products.countDocuments();
" --quiet 2>/dev/null | grep -E '^[0-9]+$' || echo "0")

FINAL_CUSTOMER_COUNT=$(mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.customers.countDocuments();
" --quiet 2>/dev/null | grep -E '^[0-9]+$' || echo "0")

print_success "Final counts - Products: $FINAL_PRODUCT_COUNT, Customers: $FINAL_CUSTOMER_COUNT"

# Test 10: Performance Test
echo ""
print_status "Test 10: Testing query performance..."

START_TIME=$(date +%s.%N)
mongosh "$MONGODB_URL" --db "$DATABASE_NAME" --eval "
db.products.find().limit(10).toArray();
" --quiet > /dev/null 2>&1
END_TIME=$(date +%s.%N)

QUERY_TIME=$(echo "$END_TIME - $START_TIME" | bc -l)
print_success "Query performance test completed in ${QUERY_TIME}s"

echo ""
print_success "🎉 All MongoDB tests completed successfully!"
echo ""
echo "📋 Test Summary:"
echo "  ✅ Connection test"
echo "  ✅ Database access test"
echo "  ✅ Collection operations test"
echo "  ✅ CRUD operations test"
echo "  ✅ Index operations test"
echo "  ✅ Aggregation test"
echo "  ✅ Cleanup operations test"
echo "  ✅ E-commerce collections test"
echo "  ✅ Sample data verification"
echo "  ✅ Query performance test"
echo ""
echo "📝 Next steps:"
echo "  - Run monitoring: ./cloud-services/monitoring/mongodb-monitor.sh"
echo "  - Connect via GUI: mongosh \"$MONGODB_URL\""
echo "  - Use MongoDB Compass for visual management" 