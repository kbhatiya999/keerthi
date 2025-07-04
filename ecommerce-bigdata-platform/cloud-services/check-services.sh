#!/bin/bash

# Load environment variables from cloud-services .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
    echo "✅ Loaded environment variables from $ENV_FILE"
else
    echo "⚠️  No .env file found at $ENV_FILE"
fi

echo "🔍 Cloud Services Health Check"
echo "=============================="
echo "Timestamp: $(date)"
echo "Purpose: Quick health check of existing services (no setup/installation)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
    esac
}

echo "📋 Checking CLI Tools:"
echo "======================"

# Check MongoDB CLI
echo -n "MongoDB CLI: "
if command -v mongosh &> /dev/null; then
    print_status "SUCCESS" "mongosh found"
else
    print_status "ERROR" "mongosh not found"
fi

# Check Confluent CLI
echo -n "Confluent CLI: "
if command -v confluent &> /dev/null; then
    print_status "SUCCESS" "confluent found"
else
    print_status "ERROR" "confluent not found"
fi

# Check Databricks CLI
echo -n "Databricks CLI: "
if command -v databricks &> /dev/null; then
    print_status "SUCCESS" "databricks found"
else
    print_status "ERROR" "databricks not found"
fi

# Check Cloudinary CLI
echo -n "Cloudinary CLI: "
if command -v cloudinary &> /dev/null; then
    print_status "SUCCESS" "cloudinary found"
else
    print_status "ERROR" "cloudinary not found"
fi

echo ""
echo "🔗 Checking Service Connections:"
echo "================================"

# Check MongoDB connection
echo -n "MongoDB Connection: "
if [ -n "$MONGODB_URL" ]; then
    if mongosh "$MONGODB_URL" --eval "db.runCommand('ping')" > /dev/null 2>&1; then
        print_status "SUCCESS" "MongoDB is accessible"
    else
        print_status "ERROR" "MongoDB connection failed"
    fi
else
    print_status "WARNING" "MongoDB URL not configured"
fi

# Check Confluent Cloud connection
echo -n "Confluent Cloud: "
if command -v confluent &> /dev/null && confluent kafka cluster list > /dev/null 2>&1; then
    print_status "SUCCESS" "Confluent Cloud is accessible"
else
    print_status "WARNING" "Confluent Cloud not configured"
fi

# Check Databricks connection
echo -n "Databricks: "
if command -v databricks &> /dev/null && databricks auth describe > /dev/null 2>&1; then
    print_status "SUCCESS" "Databricks is accessible"
else
    print_status "WARNING" "Databricks not configured"
fi

# Check Cloudinary connection
echo -n "Cloudinary: "
if command -v cloudinary &> /dev/null && cloudinary config > /dev/null 2>&1; then
    print_status "SUCCESS" "Cloudinary is accessible"
else
    print_status "WARNING" "Cloudinary not configured"
fi

echo ""
echo "📊 Summary:"
echo "==========="

# Generate dynamic summary based on actual test results
if command -v mongosh &> /dev/null && [ -n "$MONGODB_URL" ] && mongosh "$MONGODB_URL" --eval "db.runCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB: Ready"
else
    echo "❌ MongoDB: Connection failed"
fi

if command -v confluent &> /dev/null && confluent kafka cluster list > /dev/null 2>&1; then
    echo "✅ Kafka: Ready"
else
    echo "❌ Kafka: Not configured"
fi

if command -v databricks &> /dev/null && databricks auth describe > /dev/null 2>&1; then
    echo "✅ Databricks: Ready"
else
    echo "❌ Databricks: Not configured"
fi

if command -v cloudinary &> /dev/null && cloudinary config > /dev/null 2>&1; then
    echo "✅ Cloudinary: Ready"
else
    echo "❌ Cloudinary: Not configured"
fi
echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. For setup/installation: ./cloud-services/setup-all-services.sh"
echo "2. For detailed testing: Run individual test scripts"
echo "3. For monitoring: Use monitoring scripts"
echo ""
print_status "SUCCESS" "Health check completed!"
