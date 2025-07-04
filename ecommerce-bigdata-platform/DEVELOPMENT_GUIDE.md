# E-commerce Big Data Platform - Development Guide

## 🏗️ Architecture Overview

```
Frontend (Next.js) → API Route → Backend (FastAPI) → MongoDB + Kafka → Databricks
```

## 🔧 Service Configuration Tools

### 1. MongoDB Atlas

#### GUI Tools:
- **MongoDB Compass** - Official GUI for MongoDB
  - Download: https://www.mongodb.com/try/download/compass
  - Features: Visual query builder, schema analysis, performance monitoring
  - Connection: `mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/`

- **Studio 3T (formerly RoboMongo)** - Professional MongoDB GUI
  - Download: https://studio3t.com/
  - Features: Advanced query editor, data visualization, import/export

#### CLI Tools:
```bash
# Install MongoDB CLI
npm install -g mongosh

# Connect to MongoDB Atlas
mongosh "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce"

# Basic commands
show dbs                    # List databases
use ecommerce              # Switch to database
show collections           # List collections
db.products.find()         # Query products
db.orders.find().limit(5)  # Query orders with limit
```

#### Environment Variables:
```env
MONGODB_URL=mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

### 2. Confluent Cloud Kafka

#### GUI Tools:
- **Confluent Cloud Console** - Web-based management
  - URL: https://confluent.cloud/
  - Features: Topic management, schema registry, monitoring
  - Access: Use your API credentials

- **Kafka Tool** - Desktop GUI for Kafka
  - Download: https://www.kafkatool.com/
  - Features: Topic browsing, message viewing, cluster management

- **Kafka UI** - Open-source web interface
  - GitHub: https://github.com/provectus/kafka-ui
  - Features: Topic management, consumer groups, message inspection

#### CLI Tools:
```bash
# Install Confluent CLI
curl -L --http1.1 https://cnfl.io/cli | sh -s -- -b /usr/local/bin

# Login to Confluent Cloud
confluent login

# List clusters
confluent kafka cluster list

# List topics
confluent kafka topic list --cluster pkc-921jm

# Produce messages
confluent kafka topic produce clickstream --cluster pkc-921jm

# Consume messages
confluent kafka topic consume clickstream --cluster pkc-921jm --from-beginning
```

#### Environment Variables:
```env
KAFKA_BOOTSTRAP_SERVERS=pkc-921jm.us-east-2.aws.confluent.cloud:9092
KAFKA_API_KEY=XO3WPOF7B3MJM3LN
KAFKA_API_SECRET=SMJbblDfWFUdLdMtWild0IQqmTteCysFUqvKELCy4yI4aTaF9v5miTwkUfuhpikf
```

### 3. Databricks

#### GUI Tools:
- **Databricks Workspace** - Web-based interface
  - URL: https://your-workspace.cloud.databricks.com/
  - Features: Notebooks, SQL queries, ML models, dashboards

- **Databricks CLI** - Command line interface
  - Install: `pip install databricks-cli`
  - Features: Workspace management, job scheduling, cluster management

#### CLI Tools:
```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token

# List workspaces
databricks workspaces list

# Run notebook
databricks jobs submit --existing-cluster-id <cluster-id> --notebook-path /path/to/notebook

# List clusters
databricks clusters list

# Create cluster
databricks clusters create --json '{
  "cluster_name": "ecommerce-analytics",
  "spark_version": "7.3.x-scala2.12",
  "node_type_id": "Standard_DS3_v2",
  "num_workers": 2
}'
```

#### Environment Variables:
```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-personal-access-token
```

### 4. Clerk Authentication

#### GUI Tools:
- **Clerk Dashboard** - Web-based management
  - URL: https://dashboard.clerk.com/
  - Features: User management, authentication settings, webhooks

#### CLI Tools:
```bash
# Install Clerk CLI
npm install -g @clerk/cli

# Login to Clerk
clerk login

# List applications
clerk applications list

# Get user details
clerk users get <user-id>

# Create user
clerk users create --email user@example.com --password password123
```

#### Environment Variables:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_c3RpcnJpbmctcG9sZWNhdC04MS5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_ph5PGgaHb7kuND272Uyab7A0W4vxxNhHWOul3Ju8Wn
```

### 5. Cloudinary

#### GUI Tools:
- **Cloudinary Console** - Web-based management
  - URL: https://cloudinary.com/console
  - Features: Media library, transformations, analytics

#### CLI Tools:
```bash
# Install Cloudinary CLI
npm install -g cloudinary-cli

# Upload image
cloudinary upload image.jpg --folder ecommerce

# List resources
cloudinary list --type upload --max-results 10

# Transform image
cloudinary transform image.jpg --transformation "w_300,h_200,c_fill"
```

#### Environment Variables:
```env
CLOUDINARY_URL=cloudinary://785245949597287:BX5z56TipOMFmpMoDyI2RwVIPLA@dlhv5towy
CLOUDINARY_CLOUD_NAME=dlhv5towy
CLOUDINARY_API_KEY=785245949597287
CLOUDINARY_API_SECRET=BX5z56TipOMFmpMoDyI2RwVIPLA
```

## 🚀 Development Setup

### Prerequisites
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3.10-venv nodejs npm curl

# Install MongoDB CLI
npm install -g mongosh

# Install Confluent CLI
curl -L --http1.1 https://cnfl.io/cli | sh -s -- -b /usr/local/bin

# Install Databricks CLI
pip install databricks-cli

# Install Clerk CLI
npm install -g @clerk/cli

# Install Cloudinary CLI
npm install -g cloudinary-cli
```

### Project Setup
```bash
# Clone and setup
git clone <repository-url>
cd ecommerce-bigdata-platform

# Run setup script
chmod +x setup.sh
./setup.sh

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Running the Application
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 📊 Monitoring and Debugging

### Kafka Event Monitoring
```bash
# Monitor clickstream events
confluent kafka topic consume clickstream --cluster pkc-921jm --from-beginning

# Monitor order events
confluent kafka topic consume orders --cluster pkc-921jm --from-beginning

# Monitor payment events
confluent kafka topic consume payments --cluster pkc-921jm --from-beginning
```

### MongoDB Data Inspection
```bash
# Connect to MongoDB
mongosh "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce"

# Check collections
show collections

# Query recent events
db.events.find().sort({timestamp: -1}).limit(10)

# Query orders
db.orders.find().sort({_id: -1}).limit(5)
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Get products
curl http://localhost:8000/products/

# Create order
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "user123", "total_amount": 99.99, "channel": "web"}'

# Track event
curl -X POST http://localhost:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{"event_type": "add_to_cart", "customer_id": "user123", "properties": {"product_id": "123"}}'
```

## 🔍 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check network connectivity
   - Verify credentials in `.env` file
   - Ensure IP is whitelisted in MongoDB Atlas

2. **Kafka Connection Failed**
   - Verify Confluent Cloud credentials
   - Check bootstrap servers configuration
   - Ensure topics exist in Confluent Cloud

3. **Frontend Build Errors**
   - Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
   - Check TypeScript errors: `npm run lint`

4. **Backend Import Errors**
   - Activate virtual environment: `source venv/bin/activate`
   - Reinstall dependencies: `pip install -r requirements.txt`

## 📚 Additional Resources

- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Confluent Cloud Documentation](https://docs.confluent.io/cloud/current/overview.html)
- [Databricks Documentation](https://docs.databricks.com/)
- [Clerk Documentation](https://clerk.com/docs)
- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

## 🎯 Next Steps

1. Set up Databricks workspace and configure Kafka streaming
2. Implement real-time analytics dashboards
3. Add user authentication with Clerk
4. Set up image upload with Cloudinary
5. Implement payment processing
6. Add monitoring and alerting
7. Set up CI/CD pipeline 