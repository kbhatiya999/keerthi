# Confluent Cloud Kafka Setup

## Environment Variables Required

Create a `.env` file in the backend directory with the following variables:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017/ecommerce

# Confluent Cloud Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=pkc-xxxxx.us-east-1.aws.confluent.cloud:9092
KAFKA_API_KEY=your_confluent_api_key
KAFKA_API_SECRET=your_confluent_api_secret

# Backend Configuration
BACKEND_URL=http://localhost:8000
```

## Getting Confluent Cloud Credentials

1. **Sign up for Confluent Cloud** at https://www.confluent.io/confluent-cloud/
2. **Create a new cluster** (Basic plan is sufficient for development)
3. **Create API Keys**:
   - Go to API Keys section in your cluster
   - Create a new API key with "Global access"
   - Copy the API Key and Secret

## Kafka Topics

The application will automatically create these topics when events are sent:

- `clickstream` - User interaction events (add_to_cart, view_product, search)
- `orders` - Order creation and updates
- `payments` - Payment success/failure events
- `inventory` - Product creation and inventory updates
- `user_events` - General user events

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

The FastAPI server will start on http://localhost:8000

## Event Flow

1. **Frontend** sends events to `/api/events` (Next.js API route)
2. **Next.js API** forwards events to backend `/events/` endpoint
3. **Backend** stores events in MongoDB and publishes to Kafka
4. **Kafka** streams events to downstream consumers (Databricks, etc.)

## Testing Kafka Events

You can test the Kafka integration by:

1. Starting the backend server
2. Clicking "Add to Cart" on the frontend
3. Checking the backend logs for Kafka delivery confirmations
4. Viewing events in your Confluent Cloud console 