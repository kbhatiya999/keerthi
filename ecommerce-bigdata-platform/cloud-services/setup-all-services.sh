#!/bin/bash

# =============================================================================
# Cloud Services Setup Script
# =============================================================================

# Load environment variables from cloud-services .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file not found: $ENV_FILE"
    echo "   Please create cloud-services/.env with your credentials"
    exit 1
fi

echo "✅ Loading environment variables from $ENV_FILE"
source "$ENV_FILE"

echo "🚀 E-commerce Big Data Platform - Cloud Services Setup"
echo "====================================================="
echo "This script will SETUP and CONFIGURE all cloud services"
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

# Check if running in the correct directory (should be run from project root)
PROJECT_ROOT="$SCRIPT_DIR/.."
if [ ! -f "$PROJECT_ROOT/cloud-services/setup-all-services.sh" ]; then
    print_status "ERROR" "Please run this script from the project root directory"
    print_status "ERROR" "Expected: ./cloud-services/setup-all-services.sh"
    exit 1
fi

echo "📋 Services to be SETUP:"
echo "  1. ☁️  Cloudinary (Media Management)"
echo "  2. 📊 Databricks (Big Data Analytics)"
echo "  3. 📨 Kafka (Event Streaming)"
echo "  4. 🗄️  MongoDB (Database)"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run setup script for a service
run_setup() {
    local service=$1
    local setup_script=$2
    local install_command=$3
    
    echo ""
    echo "🔧 Setting up $service..."
    
    # Check if CLI is installed
    if ! command_exists "$service"; then
        print_status "WARNING" "$service CLI not installed"
        if [ -n "$install_command" ]; then
            print_status "INFO" "Installing $service CLI..."
            eval "$install_command"
        else
            print_status "ERROR" "Please install $service CLI manually"
            return 1
        fi
    fi
    
    # Run setup script if it exists
    if [ -f "$setup_script" ]; then
        print_status "INFO" "Running $service setup script..."
        if bash "$setup_script"; then
            print_status "SUCCESS" "$service setup completed"
            return 0
        else
            print_status "ERROR" "$service setup failed"
            return 1
        fi
    else
        print_status "WARNING" "Setup script not found: $setup_script"
        return 1
    fi
}

# 1. Setup Cloudinary
run_setup "cloudinary" "$SCRIPT_DIR/cloudinary/setup.sh" "npm install -g cloudinary-cli"

# 2. Setup Databricks
run_setup "databricks" "$SCRIPT_DIR/databricks/setup.sh" ""

# 3. Setup Kafka
run_setup "confluent" "$SCRIPT_DIR/kafka/setup.sh" ""

# 4. Setup MongoDB
run_setup "mongosh" "$SCRIPT_DIR/mongodb/setup.sh" ""

echo ""
echo "📊 Setup Summary:"
echo "================="
echo "| Service    | Setup Status | Notes |"
echo "|------------|--------------|-------|"

# Check setup results
if command_exists cloudinary && [ -f "$SCRIPT_DIR/cloudinary/setup.sh" ]; then
    echo "| Cloudinary | ✅         | Setup completed |"
else
    echo "| Cloudinary | ❌         | Setup failed |"
fi

if command_exists databricks && [ -f "$SCRIPT_DIR/databricks/setup.sh" ]; then
    echo "| Databricks | ✅         | Setup completed |"
else
    echo "| Databricks | ❌         | Setup failed |"
fi

if command_exists confluent && [ -f "$SCRIPT_DIR/kafka/setup.sh" ]; then
    echo "| Kafka      | ✅         | Setup completed |"
else
    echo "| Kafka      | ❌         | Setup failed |"
fi

if command_exists mongosh && [ -f "$SCRIPT_DIR/mongodb/setup.sh" ]; then
    echo "| MongoDB    | ✅         | Setup completed |"
else
    echo "| MongoDB    | ❌         | Setup failed |"
fi

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Run health check: ./cloud-services/check-services.sh"
echo "2. Test individual services with their test scripts"
echo "3. Start the backend and frontend applications"
echo ""
echo "📁 Available Scripts:"
echo "  - Health Check: ./cloud-services/check-services.sh"
echo "  - Cloudinary: ./cloud-services/cloudinary/test-cli.sh"
echo "  - Databricks: ./cloud-services/databricks/test-cli.sh"
echo "  - Kafka: ./cloud-services/kafka/test-kafka-events.sh"
echo "  - MongoDB: ./cloud-services/mongodb/test-cli.sh"
echo ""
echo "📊 Monitoring Scripts:"
echo "  - ./cloud-services/monitoring/cloudinary-monitor.sh"
echo "  - ./cloud-services/monitoring/databricks-monitor.sh"
echo "  - ./cloud-services/monitoring/kafka-monitor.sh"
echo ""
print_status "SUCCESS" "Setup process completed!" 