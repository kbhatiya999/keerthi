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
