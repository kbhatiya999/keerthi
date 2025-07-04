#!/bin/bash

echo "📊 MongoDB Atlas Monitoring"
echo "=========================="

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file not found: $ENV_FILE"
    exit 1
fi

source "$ENV_FILE"

if [ -z "$MONGODB_URL" ] || [ -z "$MONGODB_DATABASE" ]; then
    echo "❌ MongoDB configuration missing from environment file"
    exit 1
fi

DATABASE_NAME="$MONGODB_DATABASE"

# Check connection
echo "🔗 Connection Status:"
if mongosh "$MONGODB_URL" --eval "db.runCommand('ping')" --quiet > /dev/null 2>&1; then
    echo "✓ Connected to MongoDB Atlas"
else
    echo "✗ Connection failed"
    exit 1
fi

# Database stats
echo ""
echo "📈 Database Statistics:"
mongosh "$MONGODB_URL" --eval "
use $DATABASE_NAME;
print('Collections:');
db.getCollectionNames().forEach(function(collection) {
    var count = db[collection].countDocuments();
    print('  - ' + collection + ': ' + count + ' documents');
});
" --quiet

# Recent events
echo ""
echo "📝 Recent Events (last 5):"
mongosh "$MONGODB_URL" --eval "
use $DATABASE_NAME;
db.events.find().sort({timestamp: -1}).limit(5).forEach(function(event) {
    print('  - ' + event.event_type + ' by ' + event.customer_id + ' at ' + event.timestamp);
});
" --quiet

# Recent orders
echo ""
echo "🛒 Recent Orders (last 3):"
mongosh "$MONGODB_URL" --eval "
use $DATABASE_NAME;
db.orders.find().sort({_id: -1}).limit(3).forEach(function(order) {
    print('  - Order: $' + order.total_amount + ' by ' + order.customer_id);
});
" --quiet
