# Customer Feedback Sentiment Analysis Architecture

## 🎯 Overview

This document outlines the complete architecture for customer feedback sentiment analysis in the ecommerce big data platform. The system collects customer feedback, processes it using ML models in Databricks, and visualizes results in Tableau.

## 🏗️ Architecture Components

### **1. Data Collection Layer**
- **FastAPI Backend**: Collects feedback via REST API
- **MongoDB**: Stores raw feedback data and metadata
- **Kafka**: Streams raw feedback to Databricks

### **2. Processing Layer**
- **Databricks**: ML processing and sentiment analysis
- **Transformers/Hugging Face**: Pre-trained sentiment models
- **Real-time Streaming**: Kafka consumer/producer

### **3. Visualization Layer**
- **Tableau**: Interactive dashboards and reports
- **Real-time Updates**: Live sentiment monitoring
- **Historical Analysis**: Trend analysis and insights

## 📊 Data Flow

```
Customer Feedback → FastAPI → MongoDB (store) + Kafka (stream) → Databricks (analyze) → Tableau (visualize)
```

### **Step-by-Step Process:**

1. **Feedback Collection**
   - Customer submits feedback via web/mobile
   - FastAPI validates and stores in MongoDB
   - Raw feedback streamed to Kafka topic `ecommerce-feedback-raw`

2. **Sentiment Analysis**
   - Databricks consumes from Kafka
   - ML model analyzes sentiment (positive/negative/neutral)
   - Results stored back in MongoDB
   - Processed results streamed to Kafka topic `ecommerce-sentiment-analysis`

3. **Visualization**
   - Tableau connects to MongoDB for historical data
   - Real-time updates from Kafka streams
   - Interactive dashboards with filters and alerts

## 🔧 Technical Implementation

### **Backend Components**

#### **Feedback Collector** (`feedback_collector.py`)
- Collects and validates feedback data
- Stores in MongoDB with processing flags
- Streams to Kafka for real-time processing

#### **Feedback API** (`feedback_api.py`)
- REST endpoints for feedback submission
- Summary statistics and health checks
- User authentication and authorization

#### **Database Schema** (`database.py`)
```javascript
// Feedback Collection Schema
{
  "_id": ObjectId,
  "text": String,                    // Raw feedback text
  "feedback_type": String,           // review, survey, chat, support_ticket
  "rating": Number,                  // 1-5 rating (optional)
  "category": String,                // product, service, delivery, etc.
  "product_id": String,              // Associated product
  "order_id": String,                // Associated order
  "user_id": String,                 // Customer ID
  "source": String,                  // website, mobile, email, chat
  "metadata": Object,                // Additional context
  "created_at": Date,                // Feedback submission time
  "processed": Boolean,              // Databricks processing flag
  "sentiment_score": Number,         // 0-1 sentiment score
  "sentiment_label": String,         // positive, negative, neutral
  "confidence": Number,              // Model confidence (0-1)
  "keywords": Array,                 // Extracted keywords
  "processed_at": Date               // Analysis completion time
}
```

### **Databricks Processing**

#### **Sentiment Analysis Notebook** (`sentiment_analysis_notebook.py`)
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Processing**: Real-time streaming from Kafka
- **Output**: Sentiment scores, labels, keywords, confidence

#### **Key Features:**
- Pre-trained transformer model
- Real-time and batch processing
- Keyword extraction
- Confidence scoring
- Error handling and fallbacks

### **Kafka Topics**

| Topic | Purpose | Data Format |
|-------|---------|-------------|
| `ecommerce-feedback-raw` | Raw feedback from backend | JSON with feedback data |
| `ecommerce-sentiment-analysis` | Processed sentiment results | JSON with analysis results |
| `ecommerce-sentiment-summary` | Summary statistics | JSON with aggregated data |
| `ecommerce-sentiment-alerts` | Alert notifications | JSON with alert data |

## 📈 Tableau Dashboard

### **Dashboard Components:**

1. **Real-time Sentiment Overview**
   - Gauge charts for overall sentiment
   - Positive/negative/neutral distribution
   - Real-time feedback counter

2. **Sentiment Trends**
   - Time-series analysis
   - Moving averages
   - Trend identification

3. **Product Performance**
   - Product-wise sentiment analysis
   - Performance rankings
   - Improvement opportunities

4. **Keyword Analysis**
   - Word cloud visualization
   - Common themes identification
   - Sentiment correlation

5. **Source Analysis**
   - Channel performance comparison
   - Source-specific insights
   - Optimization recommendations

## 🚀 Setup Instructions

### **1. Backend Setup**
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Start the server
./scripts/start.sh
```

### **2. Kafka Topics Setup**
```bash
# Create sentiment analysis topics
cd cloud-services/kafka
./sentiment-topics.sh
```

### **3. Databricks Setup**
1. Upload `sentiment_analysis_notebook.py` to Databricks
2. Configure cluster with required packages
3. Set up job scheduling for continuous processing

### **4. Tableau Setup**
1. Connect to MongoDB Atlas
2. Import dashboard configuration
3. Set up data refresh schedules

## 🔍 API Endpoints

### **Feedback Submission**
```http
POST /feedback/submit
Content-Type: application/json
Authorization: Bearer <token>

{
  "text": "This product is amazing!",
  "feedback_type": "review",
  "rating": 5,
  "category": "product",
  "product_id": "123",
  "source": "website"
}
```

### **Feedback Summary**
```http
GET /feedback/summary?user_id=123&limit=10
Authorization: Bearer <token>
```

### **Health Check**
```http
GET /feedback/health
```

## 📊 Monitoring and Alerts

### **Real-time Alerts**
- Negative sentiment threshold alerts
- Processing time monitoring
- Data quality checks

### **Performance Metrics**
- Processing latency
- Model accuracy
- System throughput

### **Business Metrics**
- Customer satisfaction trends
- Product performance scores
- Response time analysis

## 🔒 Security Considerations

### **Data Protection**
- Encrypt sensitive feedback data
- Implement role-based access control
- Audit logging for all operations

### **API Security**
- JWT authentication
- Rate limiting
- Input validation

### **Infrastructure Security**
- Secure Kafka connections
- MongoDB access controls
- Databricks workspace security

## 🛠️ Troubleshooting

### **Common Issues**

1. **Kafka Connection Issues**
   - Verify credentials and bootstrap servers
   - Check topic existence and permissions
   - Monitor consumer group status

2. **Databricks Processing Errors**
   - Check model loading and dependencies
   - Verify MongoDB connection
   - Monitor cluster resources

3. **Tableau Data Refresh Issues**
   - Verify MongoDB connectivity
   - Check data source permissions
   - Monitor query performance

### **Debug Commands**
```bash
# Check Kafka topics
confluent kafka topic list

# Monitor feedback stream
confluent kafka topic consume ecommerce-feedback-raw --from-beginning

# Check MongoDB feedback collection
mongo "mongodb+srv://cluster0.tbyigvr.mongodb.net/ecommerce" --eval "db.feedback.find().limit(5)"
```

## 📈 Future Enhancements

### **Advanced Analytics**
- Topic modeling for feedback categorization
- Emotion detection (joy, anger, sadness, etc.)
- Intent classification (complaint, suggestion, question)

### **Machine Learning Improvements**
- Custom model training on domain data
- A/B testing for model performance
- Ensemble methods for better accuracy

### **Integration Extensions**
- CRM system integration
- Automated response generation
- Predictive analytics for customer churn

## 📚 Resources

- [Databricks Documentation](https://docs.databricks.com/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Tableau Documentation](https://help.tableau.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)

---

**Last Updated**: July 2025  
**Version**: 1.0  
**Maintainer**: Data Engineering Team 