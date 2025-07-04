# Databricks notebook source
# MAGIC %md
# MAGIC # Simple Customer Feedback Sentiment Analysis
# MAGIC 
# MAGIC This notebook reads feedback directly from MongoDB and performs sentiment analysis.
# MAGIC 
# MAGIC ## Simple Data Flow:
# MAGIC MongoDB → Databricks → MongoDB (with results) → Tableau
# MAGIC 
# MAGIC No Kafka needed!

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

# Install required packages
!pip install transformers torch pymongo pandas numpy

# COMMAND ----------

# Configuration
MONGODB_URL = "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "ecommerce"
COLLECTION_NAME = "feedback"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Sentiment Analysis Model

# COMMAND ----------

from transformers import pipeline
import torch

# Load pre-trained sentiment analysis model
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    return_all_scores=True
)

print("✅ Sentiment analysis model loaded successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Connect to MongoDB

# COMMAND ----------

import pymongo
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]
feedback_collection = db[COLLECTION_NAME]

print("✅ Connected to MongoDB")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process Unprocessed Feedback

# COMMAND ----------

def analyze_sentiment(text):
    """Analyze sentiment of text"""
    try:
        # Truncate text if too long
        if len(text) > 512:
            text = text[:512]
        
        # Perform sentiment analysis
        results = sentiment_pipeline(text)
        scores = results[0]
        
        # Extract sentiment label and score
        label_scores = {item['label']: item['score'] for item in scores}
        
        # Determine sentiment
        if 'positive' in label_scores and 'negative' in label_scores:
            if label_scores['positive'] > label_scores['negative']:
                sentiment_label = "positive"
                sentiment_score = label_scores['positive']
            else:
                sentiment_label = "negative"
                sentiment_score = label_scores['negative']
        else:
            best_label = max(label_scores, key=label_scores.get)
            sentiment_score = label_scores[best_label]
            
            if 'pos' in best_label.lower():
                sentiment_label = "positive"
            elif 'neg' in best_label.lower():
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
        
        return {
            "sentiment_label": sentiment_label,
            "sentiment_score": round(sentiment_score, 3),
            "confidence": round(sentiment_score, 3)
        }
        
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {e}")
        return {
            "sentiment_label": "neutral",
            "sentiment_score": 0.5,
            "confidence": 0.0
        }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process Feedback

# COMMAND ----------

# Find unprocessed feedback
unprocessed_feedback = feedback_collection.find({"processed": {"$ne": True}})

processed_count = 0
for feedback in unprocessed_feedback:
    try:
        feedback_id = feedback["_id"]
        text = feedback.get("text", "")
        
        print(f"📝 Processing feedback: {feedback_id}")
        
        # Perform sentiment analysis
        sentiment_result = analyze_sentiment(text)
        
        # Update MongoDB with results
        feedback_collection.update_one(
            {"_id": feedback_id},
            {
                "$set": {
                    "processed": True,
                    "sentiment_label": sentiment_result["sentiment_label"],
                    "sentiment_score": sentiment_result["sentiment_score"],
                    "confidence": sentiment_result["confidence"],
                    "processed_at": datetime.utcnow()
                }
            }
        )
        
        processed_count += 1
        print(f"✅ Processed: {sentiment_result['sentiment_label']} ({sentiment_result['sentiment_score']:.3f})")
        
    except Exception as e:
        print(f"❌ Error processing feedback: {e}")

print(f"🎉 Processing completed: {processed_count} feedback processed")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Summary Statistics

# COMMAND ----------

# Get summary statistics
pipeline = [
    {"$match": {"processed": True}},
    {"$group": {
        "_id": "$sentiment_label",
        "count": {"$sum": 1},
        "avg_score": {"$avg": "$sentiment_score"}
    }},
    {"$sort": {"count": -1}}
]

results = list(feedback_collection.aggregate(pipeline))

summary = {
    "total_processed": sum(r["count"] for r in results),
    "sentiment_distribution": {r["_id"]: r["count"] for r in results},
    "average_scores": {r["_id"]: round(r["avg_score"], 3) for r in results},
    "generated_at": datetime.utcnow().isoformat()
}

print("📊 Sentiment Analysis Summary:")
print(f"Total processed: {summary['total_processed']}")
print(f"Sentiment distribution: {summary['sentiment_distribution']}")
print(f"Average scores: {summary['average_scores']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Ready for Tableau
# MAGIC 
# MAGIC The processed feedback data is now ready for Tableau visualization:
# MAGIC 
# MAGIC - **Connection**: MongoDB Atlas
# MAGIC - **Database**: ecommerce
# MAGIC - **Collection**: feedback
# MAGIC 
# MAGIC **Key Fields for Visualization:**
# MAGIC - `sentiment_label` (positive/negative/neutral)
# MAGIC - `sentiment_score` (0-1)
# MAGIC - `confidence` (0-1)
# MAGIC - `created_at` (timestamp)
# MAGIC - `processed_at` (analysis timestamp)
# MAGIC - `feedback_type`, `category`, `product_id`, etc.

# COMMAND ----------

# Close MongoDB connection
client.close()
print("✅ MongoDB connection closed") 