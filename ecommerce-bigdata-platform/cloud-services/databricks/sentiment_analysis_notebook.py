# Databricks notebook source
# MAGIC %md
# MAGIC # Customer Feedback Sentiment Analysis
# MAGIC 
# MAGIC This notebook processes customer feedback from Kafka and performs sentiment analysis using ML models.
# MAGIC 
# MAGIC ## Data Flow:
# MAGIC 1. Read raw feedback from Kafka topic `ecommerce-feedback-raw`
# MAGIC 2. Perform sentiment analysis using pre-trained models
# MAGIC 3. Store results back to MongoDB
# MAGIC 4. Stream processed results to Kafka for real-time dashboards
# MAGIC 
# MAGIC ## Tech Stack:
# MAGIC - **Kafka**: Raw feedback streaming
# MAGIC - **Databricks**: ML processing and analysis
# MAGIC - **MongoDB**: Store processed results
# MAGIC - **Tableau**: Visualization dashboard

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration

# COMMAND ----------

# Install required packages
!pip install transformers torch pandas numpy pymongo kafka-python

# COMMAND ----------

# Configuration
KAFKA_BOOTSTRAP_SERVERS = "pkc-921jm.us-east-2.aws.confluent.cloud:9092"
KAFKA_API_KEY = "F2EPAIQ65RPUCIBT"
KAFKA_API_SECRET = "O81+QXfXu7ZZKg44Jv8ZhvAylEsUkv1RmPAHTZeif42kJTKQOCJu5G6uWQlXZYYM"
MONGODB_URL = "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Kafka Topics
RAW_FEEDBACK_TOPIC = "ecommerce-feedback-raw"
SENTIMENT_RESULTS_TOPIC = "ecommerce-sentiment-analysis"
SENTIMENT_SUMMARY_TOPIC = "ecommerce-sentiment-summary"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Sentiment Analysis Model

# COMMAND ----------

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load pre-trained sentiment analysis model
@dbutils.fs.mkdirs("/tmp/models")
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Download and cache the model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Create sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    return_all_scores=True
)

print("✅ Sentiment analysis model loaded successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Kafka Consumer Setup

# COMMAND ----------

from kafka import KafkaConsumer
import json
from datetime import datetime
import pymongo

# Setup Kafka consumer
consumer = KafkaConsumer(
    RAW_FEEDBACK_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SASL_SSL",
    sasl_mechanism="PLAIN",
    sasl_plain_username=KAFKA_API_KEY,
    sasl_plain_password=KAFKA_API_SECRET,
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='sentiment-analysis-group'
)

# Setup MongoDB connection
mongo_client = pymongo.MongoClient(MONGODB_URL)
db = mongo_client.ecommerce
feedback_collection = db.feedback

print("✅ Kafka consumer and MongoDB connection established")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sentiment Analysis Function

# COMMAND ----------

def analyze_sentiment(text):
    """
    Analyze sentiment of text using the loaded model
    """
    try:
        # Truncate text if too long for model
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        # Perform sentiment analysis
        results = sentiment_pipeline(text)
        
        # Extract scores
        scores = results[0]
        label_scores = {item['label']: item['score'] for item in scores}
        
        # Determine sentiment label and score
        if 'positive' in label_scores and 'negative' in label_scores:
            if label_scores['positive'] > label_scores['negative']:
                sentiment_label = "positive"
                sentiment_score = label_scores['positive']
            else:
                sentiment_label = "negative"
                sentiment_score = label_scores['negative']
        else:
            # Handle different label formats
            best_label = max(label_scores, key=label_scores.get)
            sentiment_score = label_scores[best_label]
            
            # Map labels to standard format
            if 'pos' in best_label.lower() or 'positive' in best_label.lower():
                sentiment_label = "positive"
            elif 'neg' in best_label.lower() or 'negative' in best_label.lower():
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
        
        # Extract keywords (simple approach - can be enhanced)
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        keywords = [word for word in words if word not in common_words and len(word) > 3][:5]
        
        return {
            "sentiment_label": sentiment_label,
            "sentiment_score": round(sentiment_score, 3),
            "confidence": round(sentiment_score, 3),
            "keywords": keywords,
            "model_used": model_name
        }
        
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {e}")
        return {
            "sentiment_label": "neutral",
            "sentiment_score": 0.5,
            "confidence": 0.0,
            "keywords": [],
            "model_used": "error"
        }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process Feedback Stream

# COMMAND ----------

from kafka import KafkaProducer
import time

# Setup Kafka producer for results
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SASL_SSL",
    sasl_mechanism="PLAIN",
    sasl_plain_username=KAFKA_API_KEY,
    sasl_plain_password=KAFKA_API_SECRET,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None
)

print("🚀 Starting sentiment analysis processing...")
print("📊 Listening for feedback on topic:", RAW_FEEDBACK_TOPIC)

# Process messages
try:
    for message in consumer:
        try:
            # Parse feedback data
            feedback_data = message.value
            feedback_id = feedback_data.get('feedback_id')
            text = feedback_data.get('text', '')
            
            print(f"📝 Processing feedback: {feedback_id}")
            
            # Perform sentiment analysis
            sentiment_result = analyze_sentiment(text)
            
            # Prepare result data
            result_data = {
                "feedback_id": feedback_id,
                "text": text,
                "feedback_type": feedback_data.get('feedback_type'),
                "user_id": feedback_data.get('user_id'),
                "product_id": feedback_data.get('product_id'),
                "order_id": feedback_data.get('order_id'),
                "sentiment_label": sentiment_result["sentiment_label"],
                "sentiment_score": sentiment_result["sentiment_score"],
                "confidence": sentiment_result["confidence"],
                "keywords": sentiment_result["keywords"],
                "model_used": sentiment_result["model_used"],
                "processed_at": datetime.utcnow().isoformat(),
                "event_type": "sentiment_analyzed"
            }
            
            # Update MongoDB
            feedback_collection.update_one(
                {"_id": feedback_id},
                {
                    "$set": {
                        "processed": True,
                        "sentiment_label": sentiment_result["sentiment_label"],
                        "sentiment_score": sentiment_result["sentiment_score"],
                        "confidence": sentiment_result["confidence"],
                        "keywords": sentiment_result["keywords"],
                        "processed_at": datetime.utcnow()
                    }
                }
            )
            
            # Send to Kafka
            producer.send(
                SENTIMENT_RESULTS_TOPIC,
                key=feedback_id,
                value=result_data
            )
            
            print(f"✅ Sentiment analysis completed: {sentiment_result['sentiment_label']} ({sentiment_result['sentiment_score']:.3f})")
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            continue

except KeyboardInterrupt:
    print("🛑 Stopping sentiment analysis processing...")
finally:
    consumer.close()
    producer.close()
    mongo_client.close()
    print("✅ Cleanup completed")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Batch Processing (Alternative)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Process Historical Feedback
# MAGIC 
# MAGIC This section can be used to process existing feedback in MongoDB that hasn't been analyzed yet.

# COMMAND ----------

def process_historical_feedback():
    """
    Process all unprocessed feedback in MongoDB
    """
    # Find unprocessed feedback
    unprocessed_feedback = feedback_collection.find({"processed": {"$ne": True}})
    
    processed_count = 0
    for feedback in unprocessed_feedback:
        try:
            feedback_id = str(feedback["_id"])
            text = feedback.get("text", "")
            
            print(f"📝 Processing historical feedback: {feedback_id}")
            
            # Perform sentiment analysis
            sentiment_result = analyze_sentiment(text)
            
            # Update MongoDB
            feedback_collection.update_one(
                {"_id": feedback["_id"]},
                {
                    "$set": {
                        "processed": True,
                        "sentiment_label": sentiment_result["sentiment_label"],
                        "sentiment_score": sentiment_result["sentiment_score"],
                        "confidence": sentiment_result["confidence"],
                        "keywords": sentiment_result["keywords"],
                        "processed_at": datetime.utcnow()
                    }
                }
            )
            
            processed_count += 1
            print(f"✅ Processed: {sentiment_result['sentiment_label']}")
            
        except Exception as e:
            print(f"❌ Error processing {feedback_id}: {e}")
    
    print(f"🎉 Batch processing completed: {processed_count} feedback processed")

# Uncomment to run batch processing
# process_historical_feedback()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Summary Statistics

# COMMAND ----------

def generate_sentiment_summary():
    """
    Generate summary statistics for sentiment analysis
    """
    pipeline = [
        {"$match": {"processed": True}},
        {"$group": {
            "_id": "$sentiment_label",
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$sentiment_score"},
            "avg_confidence": {"$avg": "$confidence"}
        }},
        {"$sort": {"count": -1}}
    ]
    
    results = list(feedback_collection.aggregate(pipeline))
    
    summary = {
        "total_processed": sum(r["count"] for r in results),
        "sentiment_distribution": {r["_id"]: r["count"] for r in results},
        "average_scores": {r["_id"]: round(r["avg_score"], 3) for r in results},
        "average_confidence": {r["_id"]: round(r["avg_confidence"], 3) for r in results},
        "generated_at": datetime.utcnow().isoformat()
    }
    
    # Send summary to Kafka
    producer.send(
        SENTIMENT_SUMMARY_TOPIC,
        key="summary",
        value=summary
    )
    
    print("📊 Sentiment summary generated and sent to Kafka")
    return summary

# Generate summary
summary = generate_sentiment_summary()
display(summary) 