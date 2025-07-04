#!/bin/bash

echo "📊 E-commerce Platform - Cloud Services Monitoring"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check service health
check_service_health() {
    local service_name="$1"
    local check_command="$2"
    
    echo -n "  $service_name: "
    if eval "$check_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Function to display service statistics
show_service_stats() {
    local service_name="$1"
    local stats_command="$2"
    
    echo -e "${CYAN}$service_name Statistics:${NC}"
    eval "$stats_command" 2>/dev/null || echo "  Unable to retrieve statistics"
    echo ""
}

# Main monitoring function
monitor_all_services() {
    print_header "🔍 Service Health Check"
    echo "=========================="
    
    local all_healthy=true
    
    # Check MongoDB
    if check_service_health "MongoDB Atlas" "mongosh 'mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce' --eval 'db.runCommand(\"ping\")' --quiet"; then
        show_service_stats "MongoDB" "mongosh 'mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce' --eval 'db.getCollectionNames().forEach(function(c) { print(\"  - \" + c + \": \" + db[c].countDocuments() + \" documents\") })' --quiet"
    else
        all_healthy=false
    fi
    
    # Check Confluent Cloud
    if check_service_health "Confluent Cloud" "confluent kafka cluster list"; then
        show_service_stats "Kafka" "confluent kafka topic list --cluster pkc-921jm"
    else
        all_healthy=false
    fi
    
    # Check if tools are installed
    print_header "🛠️ Tool Installation Status"
    echo "=============================="
    
    local tools=("mongosh" "confluent" "databricks" "cloudinary")
    for tool in "${tools[@]}"; do
        echo -n "  $tool: "
        if command_exists "$tool"; then
            echo -e "${GREEN}✓ Installed${NC}"
        else
            echo -e "${RED}✗ Not installed${NC}"
            all_healthy=false
        fi
    done
    
    echo ""
    if [ "$all_healthy" = true ]; then
        print_success "🎉 All services are healthy!"
    else
        print_warning "⚠️ Some services need attention"
    fi
}

# Real-time monitoring function
start_realtime_monitoring() {
    print_header "📡 Real-time Event Monitoring"
    echo "================================"
    
    echo "Starting real-time monitoring..."
    echo "Press Ctrl+C to stop"
    echo ""
    
    # Start monitoring Kafka events in background
    (
        echo -e "${CYAN}📊 Kafka Events (clickstream):${NC}"
        confluent kafka topic consume clickstream --cluster pkc-921jm --from-beginning --timeout-ms 5000 2>/dev/null | head -10
    ) &
    
    (
        echo -e "${CYAN}🛒 Kafka Events (orders):${NC}"
        confluent kafka topic consume orders --cluster pkc-921jm --from-beginning --timeout-ms 5000 2>/dev/null | head -10
    ) &
    
    # Wait for background processes
    wait
}

# Dashboard function
show_dashboard() {
    clear
    print_header "📊 E-commerce Platform Dashboard"
    echo "====================================="
    echo ""
    
    # Current time
    echo -e "${BLUE}🕐 Last Updated:${NC} $(date)"
    echo ""
    
    # Service health
    monitor_all_services
    
    # Quick stats
    print_header "📈 Quick Statistics"
    echo "===================="
    
    # MongoDB stats
    echo -e "${CYAN}🗄️ Database:${NC}"
    mongosh "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce" --eval "
    print('  Collections:');
    db.getCollectionNames().forEach(function(c) {
        var count = db[c].countDocuments();
        print('    - ' + c + ': ' + count + ' documents');
    });
    " --quiet 2>/dev/null || echo "  Unable to connect to MongoDB"
    
    echo ""
    
    # Kafka stats
    echo -e "${CYAN}📡 Kafka Topics:${NC}"
    confluent kafka topic list --cluster pkc-921jm 2>/dev/null | grep -E "(clickstream|orders|payments)" | while read topic; do
        echo "    - $topic"
    done || echo "  Unable to connect to Kafka"
    
    echo ""
    
    # Recent activity
    print_header "🔄 Recent Activity"
    echo "==================="
    
    # Recent events from MongoDB
    echo -e "${CYAN}📝 Recent Events:${NC}"
    mongosh "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce" --eval "
    db.events.find().sort({timestamp: -1}).limit(3).forEach(function(event) {
        print('    - ' + event.event_type + ' by ' + event.customer_id + ' at ' + event.timestamp);
    });
    " --quiet 2>/dev/null || echo "  No recent events found"
    
    echo ""
    
    # Recent orders
    echo -e "${CYAN}🛒 Recent Orders:${NC}"
    mongosh "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce" --eval "
    db.orders.find().sort({_id: -1}).limit(3).forEach(function(order) {
        print('    - $' + order.total_amount + ' by ' + order.customer_id);
    });
    " --quiet 2>/dev/null || echo "  No recent orders found"
}

# Main menu
show_menu() {
    echo ""
    print_header "🎛️ Monitoring Menu"
    echo "==================="
    echo "1. Service Health Check"
    echo "2. Real-time Event Monitoring"
    echo "3. Dashboard View"
    echo "4. MongoDB Monitor"
    echo "5. Kafka Monitor"
    echo "6. Exit"
    echo ""
    read -p "Select an option (1-6): " choice
    
    case $choice in
        1)
            monitor_all_services
            ;;
        2)
            start_realtime_monitoring
            ;;
        3)
            show_dashboard
            ;;
        4)
            ./mongodb-monitor.sh
            ;;
        5)
            ./kafka-monitor.sh
            ;;
        6)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
}

# Check if running in interactive mode
if [ "$1" = "--dashboard" ]; then
    show_dashboard
elif [ "$1" = "--health" ]; then
    monitor_all_services
elif [ "$1" = "--realtime" ]; then
    start_realtime_monitoring
else
    # Interactive mode
    while true; do
        show_menu
        echo ""
        read -p "Press Enter to continue..."
    done
fi 