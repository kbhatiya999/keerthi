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
