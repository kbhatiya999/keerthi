#!/bin/bash

# =============================================================================
# Databricks Community Edition Setup
# =============================================================================

# Load environment variables from cloud-services .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file not found: $ENV_FILE"
    echo "   Please create cloud-services/.env with your Databricks credentials"
    exit 1
fi

echo "✅ Loading environment variables from $ENV_FILE"
source "$ENV_FILE"

# Install the new official Databricks CLI (recommended)
echo "[INFO] Installing the latest Databricks CLI (standalone binary)..."
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sudo sh

echo "🔧 Databricks Community Edition Setup"
echo "===================================="

# Use environment variables from .env
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "❌ DATABRICKS_HOST or DATABRICKS_TOKEN not set in cloud-services/.env"
    echo "   Please add your Databricks credentials to cloud-services/.env"
    exit 1
fi

echo "[INFO] Using Databricks Host: $DATABRICKS_HOST"

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

echo "[INFO] Configuring Databricks CLI..."

# Create configuration directory and file for new CLI
echo "[INFO] Setting up authentication configuration..."
mkdir -p ~/.databricks

# Create config.json for new CLI authentication
cat > ~/.databricks/config.json << EOF
{
  "hosts": {
    "$DATABRICKS_HOST": {
      "auth_type": "pat",
      "personal_access_token": "$DATABRICKS_TOKEN"
    }
  }
}
EOF

echo "[INFO] Configuration file created at ~/.databricks/config.json"

# Test connection with new CLI
echo "[INFO] Testing Databricks connection with new CLI..."
if databricks auth describe > /dev/null 2>&1; then
    echo "[SUCCESS] Databricks connection successful with new CLI"
    
    echo "[INFO] Authentication details:"
    databricks auth describe
    
    echo "[INFO] Listing all clusters..."
    databricks clusters list
    
    echo "[INFO] Checking cluster count..."
    CLUSTER_COUNT=$(databricks clusters list --output JSON 2>/dev/null | jq -r '.clusters | length' 2>/dev/null || echo "0")
    echo "[INFO] Number of clusters: $CLUSTER_COUNT"
    
else
    echo "[ERROR] Failed to connect to Databricks with new CLI"
    echo "[INFO] Please check your credentials and try again"
    echo ""
    echo "📋 How to get Community Edition credentials:"
    echo "  1. Go to: https://community.cloud.databricks.com"
    echo "  2. Sign up for free Community Edition"
    echo "  3. Copy your workspace URL (Host)"
    echo "  4. Generate access token: User Settings → Generate New Token"
    echo "  5. Update cloud-services/.env with your credentials"
fi

echo ""
echo "[SUCCESS] 🎉 Databricks Community Edition setup complete!"
echo ""
echo "📋 Available commands:"
echo "  - List clusters: databricks clusters list"
echo "  - Get cluster info: databricks clusters get --cluster-id <cluster-id>"
echo "  - Start cluster: databricks clusters start --cluster-id <cluster-id>"
echo "  - Stop cluster: databricks clusters delete --cluster-id <cluster-id>"
echo "  - Check auth: databricks auth describe"
echo "  - GUI: $DATABRICKS_HOST"
echo ""
echo "💡 Community Edition Limitations:"
echo "  - Single-user workspace"
echo "  - Limited compute resources"
echo "  - Perfect for learning and small projects"
echo ""
echo "🔧 New CLI Features:"
echo "  - Version: $(databricks version)"
echo "  - More secure authentication"
echo "  - Better error handling"
echo "  - Enhanced command structure" 