#!/bin/bash

echo "🧪 Databricks CLI Test Script"
echo "============================"

# Check if Databricks CLI is installed
if ! command -v databricks &> /dev/null; then
    echo "[ERROR] Databricks CLI not found. Please install it first."
    exit 1
fi

echo "[INFO] Databricks CLI version:"
databricks version

echo ""
echo "[INFO] Testing authentication..."
if databricks auth describe > /dev/null 2>&1; then
    echo "[SUCCESS] Authentication successful"
    echo "[INFO] Authentication details:"
    databricks auth describe
else
    echo "[ERROR] Authentication failed"
    exit 1
fi

echo ""
echo "[INFO] Testing workspace access..."
if databricks workspace list > /dev/null 2>&1; then
    echo "[SUCCESS] Workspace access successful"
    echo "[INFO] Workspace contents:"
    databricks workspace list
else
    echo "[WARNING] Workspace access failed (this is normal for Community Edition)"
fi

echo ""
echo "[INFO] Testing cluster operations..."
echo "[INFO] Listing clusters:"
CLUSTERS=$(databricks clusters list --output JSON 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "[SUCCESS] Cluster listing successful"
    echo "$CLUSTERS" | jq '.' 2>/dev/null || echo "$CLUSTERS"
else
    echo "[WARNING] Cluster listing failed"
fi

echo ""
echo "[INFO] Testing SQL warehouse access..."
if databricks warehouses list > /dev/null 2>&1; then
    echo "[SUCCESS] SQL warehouse access successful"
    echo "[INFO] Available warehouses:"
    databricks warehouses list
else
    echo "[WARNING] SQL warehouse access failed (this is normal for Community Edition)"
fi

echo ""
echo "[INFO] Testing user information..."
if databricks current-user > /dev/null 2>&1; then
    echo "[SUCCESS] User info access successful"
    echo "[INFO] Current user:"
    databricks current-user
else
    echo "[WARNING] User info access failed"
fi

echo ""
echo "[INFO] Testing workspace settings..."
if databricks settings list > /dev/null 2>&1; then
    echo "[SUCCESS] Settings access successful"
    echo "[INFO] Workspace settings:"
    databricks settings list
else
    echo "[WARNING] Settings access failed"
fi

echo ""
echo "[SUCCESS] 🎉 Databricks CLI test completed!"
echo ""
echo "📋 Available commands for Community Edition:"
echo "  - List clusters: databricks clusters list"
echo "  - Create cluster: databricks clusters create --json-file cluster-config.json"
echo "  - Start cluster: databricks clusters start --cluster-id <id>"
echo "  - Stop cluster: databricks clusters delete --cluster-id <id>"
echo "  - List workspace: databricks workspace list"
echo "  - Create notebook: databricks workspace import --path /path/to/notebook --language PYTHON"
echo "  - Check auth: databricks auth describe"
echo "  - Get user info: databricks current-user"
echo ""
echo "💡 Community Edition Limitations:"
echo "  - Single-user workspace"
echo "  - Limited compute resources"
echo "  - Some enterprise features not available"
echo ""
echo "🔗 Access your workspace at: https://dbc-27febc87-68f1.cloud.databricks.com" 