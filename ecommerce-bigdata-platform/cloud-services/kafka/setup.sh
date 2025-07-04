#!/bin/bash

# =============================================================================
# Confluent Cloud Kafka Setup
# =============================================================================

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file not found: $ENV_FILE"
    exit 1
fi

echo "✅ Loading environment variables from $ENV_FILE"
source "$ENV_FILE"

echo "📡 Confluent Cloud Kafka Setup"
echo "=============================="

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

# Use environment variables from .env
if [ -z "$KAFKA_BOOTSTRAP_SERVERS" ] || [ -z "$KAFKA_API_KEY" ] || [ -z "$KAFKA_API_SECRET" ]; then
    print_error "Kafka credentials not set in cloud-services/.env"
    echo "   Please add KAFKA_BOOTSTRAP_SERVERS, KAFKA_API_KEY, and KAFKA_API_SECRET to cloud-services/.env"
    exit 1
fi

# Confluent Cloud Configuration
CLUSTER_ID="lkc-dxp5o1"
API_KEY="$KAFKA_API_KEY"
API_SECRET="$KAFKA_API_SECRET"
BOOTSTRAP_SERVERS="$KAFKA_BOOTSTRAP_SERVERS"

print_status "Using Kafka Bootstrap Servers: $BOOTSTRAP_SERVERS"

# Check if confluent CLI is installed
if ! command -v confluent &> /dev/null; then
    print_error "Confluent CLI not found. Please run ./cloud-services/setup-all-services.sh first"
    exit 1
fi

print_status "Testing Confluent Cloud connection..."
# Store and use API key for authentication
confluent api-key store "$API_KEY" "$API_SECRET" --resource "$CLUSTER_ID" > /dev/null 2>&1
confluent api-key use "$API_KEY" --resource "$CLUSTER_ID" > /dev/null 2>&1

# Set the active cluster
if confluent kafka cluster use "$CLUSTER_ID" > /dev/null 2>&1; then
    print_success "Active cluster set to $CLUSTER_ID"
else
    print_warning "Could not set active cluster, but API key stored"
fi

# Create topics
print_status "Creating Kafka topics..."

TOPICS=("clickstream" "orders" "payments" "inventory" "user_events")

for topic in "${TOPICS[@]}"; do
    print_status "Creating topic: $topic"
    if confluent kafka topic create "$topic" --partitions 3 > /dev/null 2>&1; then
        print_success "Topic '$topic' created successfully"
    else
        print_warning "Topic '$topic' might already exist or creation failed"
    fi
done

# Create topic configuration
cat > kafka-topics-config.json << EOF
{
  "topics": {
    "clickstream": {
      "description": "User interaction events (add_to_cart, view_product, search)",
      "partitions": 3,
      "replication_factor": 3,
      "configs": {
        "retention.ms": "604800000",
        "cleanup.policy": "delete"
      }
    },
    "orders": {
      "description": "Order creation and updates",
      "partitions": 3,
      "replication_factor": 3,
      "configs": {
        "retention.ms": "2592000000",
        "cleanup.policy": "delete"
      }
    },
    "payments": {
      "description": "Payment success/failure events",
      "partitions": 3,
      "replication_factor": 3,
      "configs": {
        "retention.ms": "2592000000",
        "cleanup.policy": "delete"
      }
    },
    "inventory": {
      "description": "Product creation and inventory updates",
      "partitions": 3,
      "replication_factor": 3,
      "configs": {
        "retention.ms": "2592000000",
        "cleanup.policy": "delete"
      }
    },
    "user_events": {
      "description": "General user events",
      "partitions": 3,
      "replication_factor": 3,
      "configs": {
        "retention.ms": "604800000",
        "cleanup.policy": "delete"
      }
    }
  }
}
EOF

print_success "Topic configuration saved to kafka-topics-config.json"

# Create monitoring script
cat > ../monitoring/kafka-monitor.sh << 'EOF'
#!/bin/bash

echo "📡 Kafka Event Monitoring"
echo "========================"

CLUSTER_ID="lkc-dxp5o1"
TOPICS=("clickstream" "orders" "payments" "inventory" "user_events")

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check connection
echo "🔗 Connection Status:"
if confluent kafka cluster list > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Connected to Confluent Cloud${NC}"
else
    echo -e "${RED}✗ Connection failed${NC}"
    exit 1
fi

# List topics
echo ""
echo "📋 Available Topics:"
confluent kafka topic list

# Topic statistics
echo ""
echo "�� Topic Statistics:"
for topic in "${TOPICS[@]}"; do
    echo -n "  $topic: "
    if confluent kafka topic describe "$topic" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Active${NC}"
    else
        echo -e "${RED}✗ Not found${NC}"
    fi
done

# Consumer groups
echo ""
echo "👥 Consumer Groups:"
confluent kafka consumer-group list 2>/dev/null || echo "  No consumer groups found"

echo ""
echo "📝 To monitor events in real-time:"
echo "  confluent kafka topic consume clickstream --from-beginning"
echo "  confluent kafka topic consume orders --from-beginning"
echo "  confluent kafka topic consume payments --from-beginning"
EOF

chmod +x ../monitoring/kafka-monitor.sh

# Create event producer test script
cat > test-kafka-events.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing Kafka Event Production"
echo "================================="

CLUSTER_ID="lkc-dxp5o1"

# Test clickstream event
echo "📊 Producing clickstream event..."
echo '{"event_type": "add_to_cart", "customer_id": "test_user", "product_id": "123", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' | \
confluent kafka topic produce clickstream

# Test order event
echo "🛒 Producing order event..."
echo '{"event_type": "order_created", "customer_id": "test_user", "order_id": "order_123", "total_amount": 99.99, "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' | \
confluent kafka topic produce orders

# Test payment event
echo "💳 Producing payment event..."
echo '{"event_type": "payment_success", "customer_id": "test_user", "order_id": "order_123", "amount": 99.99, "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' | \
confluent kafka topic produce payments

echo ""
echo "✅ Test events produced successfully!"
echo "📝 Check events in Confluent Cloud console or run:"
echo "  confluent kafka topic consume clickstream --from-beginning"
EOF

chmod +x test-kafka-events.sh

print_success "Kafka monitoring and test scripts created"

echo ""
print_success "🎉 Confluent Cloud Kafka setup complete!"
echo ""
echo "📋 Available commands:"
echo "  - List topics: confluent kafka topic list"
echo "  - Monitor events: ./cloud-services/monitoring/kafka-monitor.sh"
echo "  - Test events: ./cloud-services/kafka/test-kafka-events.sh"
echo "  - GUI: https://confluent.cloud/ (web console)"
echo ""
echo "🔧 Configuration:"
echo "  - Cluster ID: $CLUSTER_ID"
echo "  - Bootstrap Servers: $BOOTSTRAP_SERVERS"
echo "  - API Key: $API_KEY" 