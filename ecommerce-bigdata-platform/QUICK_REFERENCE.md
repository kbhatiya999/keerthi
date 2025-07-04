# Quick Reference - E-commerce Big Data Platform

## 🚀 Quick Start Commands

### Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

### Frontend
```bash
cd frontend
npm run dev
```

## 📊 Service Monitoring Commands

### MongoDB
```bash
# Connect to MongoDB Atlas
mongosh "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce"

# Quick queries
show collections
db.products.find().limit(5)
db.orders.find().sort({_id: -1}).limit(3)
db.events.find().sort({timestamp: -1}).limit(10)
```

### Kafka
```bash
# Login to Confluent Cloud
confluent login

# List topics
confluent kafka topic list --cluster pkc-921jm

# Monitor events in real-time
confluent kafka topic consume clickstream --cluster pkc-921jm --from-beginning
confluent kafka topic consume orders --cluster pkc-921jm --from-beginning
confluent kafka topic consume payments --cluster pkc-921jm --from-beginning
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Get all products
curl http://localhost:8000/products/

# Create test order
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "test123", "total_amount": 49.99, "channel": "web"}'

# Track test event
curl -X POST http://localhost:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{"event_type": "add_to_cart", "customer_id": "test123", "properties": {"product_id": "123"}}'
```

## 🔧 Environment Variables

### Backend (.env)
```env
MONGODB_URL=mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
KAFKA_BOOTSTRAP_SERVERS=pkc-921jm.us-east-2.aws.confluent.cloud:9092
KAFKA_API_KEY=XO3WPOF7B3MJM3LN
KAFKA_API_SECRET=SMJbblDfWFUdLdMtWild0IQqmTteCysFUqvKELCy4yI4aTaF9v5miTwkUfuhpikf
BACKEND_URL=http://localhost:8000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
CLOUDINARY_CLOUD_NAME=dlhv5towy
CLOUDINARY_API_KEY=785245949597287
CLOUDINARY_API_SECRET=BX5z56TipOMFmpMoDyI2RwVIPLA
BACKEND_URL=http://localhost:8000
```

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB Atlas**: https://cloud.mongodb.com/
- **Confluent Cloud**: https://confluent.cloud/
- **Cloudinary Console**: https://cloudinary.com/console

## 🔍 Debugging Commands

### Check if services are running
```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check MongoDB connection
mongosh "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce" --eval "db.runCommand('ping')"
```

### View logs
```bash
# Backend logs (in backend directory with venv activated)
python main.py

# Frontend logs (in frontend directory)
npm run dev
```

### Reset environment
```bash
# Backend
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📝 Common Tasks

### Add a new product
```bash
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "price": 29.99, "description": "A test product"}'
```

### Monitor Kafka events
```bash
# In a separate terminal
confluent kafka topic consume clickstream --cluster pkc-921jm --from-beginning
```

### Check database collections
```bash
mongosh "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce" --eval "show collections"
```

### Test event tracking
```bash
# Click "Add to Cart" on frontend, then check:
# 1. Backend logs for Kafka delivery
# 2. MongoDB for event storage
# 3. Confluent Cloud console for messages
``` 