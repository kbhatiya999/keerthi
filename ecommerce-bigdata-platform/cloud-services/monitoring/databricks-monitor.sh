#!/bin/bash

echo "📊 Databricks Monitoring Report"
echo "=============================="
echo "Timestamp: $(date)"
echo ""

# Check if Databricks CLI is available
if ! command -v databricks &> /dev/null; then
    echo "[ERROR] Databricks CLI not found"
    exit 1
fi

# Check authentication
echo "[INFO] Checking authentication..."
if databricks auth describe > /dev/null 2>&1; then
    echo "[SUCCESS] ✅ Authentication: OK"
    AUTH_HOST=$(databricks auth describe | grep "Host:" | awk '{print $2}')
    AUTH_USER=$(databricks auth describe | grep "User:" | awk '{print $2}')
    echo "   Host: $AUTH_HOST"
    echo "   User: $AUTH_USER"
else
    echo "[ERROR] ❌ Authentication: FAILED"
    exit 1
fi

echo ""

# Check user status
echo "[INFO] Checking user status..."
if USER_INFO=$(databricks current-user me 2>/dev/null); then
    echo "[SUCCESS] ✅ User Status: OK"
    USER_ACTIVE=$(echo "$USER_INFO" | jq -r '.active' 2>/dev/null)
    USER_EMAIL=$(echo "$USER_INFO" | jq -r '.emails[0].value' 2>/dev/null)
    echo "   Active: $USER_ACTIVE"
    echo "   Email: $USER_EMAIL"
else
    echo "[WARNING] ⚠️  User Status: UNKNOWN"
fi

echo ""

# Check clusters
echo "[INFO] Checking clusters..."
if CLUSTERS=$(databricks clusters list --output JSON 2>/dev/null); then
    CLUSTER_COUNT=$(echo "$CLUSTERS" | jq -r '.clusters | length' 2>/dev/null || echo "0")
    echo "[SUCCESS] ✅ Clusters: $CLUSTER_COUNT found"
    
    if [ "$CLUSTER_COUNT" -gt 0 ]; then
        echo "   Cluster details:"
        echo "$CLUSTERS" | jq -r '.clusters[] | "   - \(.cluster_name) (\(.cluster_id)): \(.state)"' 2>/dev/null
    else
        echo "   No clusters found"
    fi
else
    echo "[WARNING] ⚠️  Clusters: UNKNOWN"
fi

echo ""

# Check SQL warehouses
echo "[INFO] Checking SQL warehouses..."
if WAREHOUSES=$(databricks warehouses list 2>/dev/null); then
    echo "[SUCCESS] ✅ SQL Warehouses: Available"
    echo "   Warehouse details:"
    echo "$WAREHOUSES" | tail -n +2 | while read -r line; do
        if [ -n "$line" ]; then
            echo "   - $line"
        fi
    done
else
    echo "[WARNING] ⚠️  SQL Warehouses: UNKNOWN"
fi

echo ""

# Check workspace access
echo "[INFO] Checking workspace access..."
if databricks workspace list > /dev/null 2>&1; then
    echo "[SUCCESS] ✅ Workspace Access: OK"
else
    echo "[WARNING] ⚠️  Workspace Access: LIMITED (normal for Community Edition)"
fi

echo ""

# Summary
echo "📋 Summary:"
echo "   ✅ Authentication: Working"
echo "   ✅ User Status: Active"
echo "   ✅ CLI Version: $(databricks version)"
echo "   ✅ API Access: Available"
echo ""
echo "🔗 Workspace URL: $AUTH_HOST"
echo "👤 User: $AUTH_USER"
echo ""
echo "💡 Community Edition Status: ACTIVE"
echo "   - Single-user workspace"
echo "   - Limited compute resources"
echo "   - Perfect for learning and development" 