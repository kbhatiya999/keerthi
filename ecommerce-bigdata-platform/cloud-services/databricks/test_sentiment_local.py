#!/usr/bin/env python3
"""
Local test script for sentiment analysis
This will process feedback from MongoDB and update it with sentiment results
"""

import pymongo
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URL = "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "ecommerce"
COLLECTION_NAME = "feedback"

def simple_sentiment_analysis(text):
    """
    Simple rule-based sentiment analysis for testing
    In production, this would be replaced with ML model
    """
    text_lower = text.lower()
    
    # Positive words
    positive_words = ['amazing', 'love', 'great', 'excellent', 'good', 'helpful', 'wonderful', 'fantastic', 'perfect']
    
    # Negative words
    negative_words = ['bad', 'terrible', 'awful', 'slow', 'damaged', 'poor', 'disappointed', 'hate', 'worst']
    
    # Count positive and negative words
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Simple scoring
    if positive_count > negative_count:
        sentiment_label = "positive"
        sentiment_score = min(0.9, 0.5 + (positive_count * 0.1))
    elif negative_count > positive_count:
        sentiment_label = "negative"
        sentiment_score = min(0.9, 0.5 + (negative_count * 0.1))
    else:
        sentiment_label = "neutral"
        sentiment_score = 0.5
    
    return {
        "sentiment_label": sentiment_label,
        "sentiment_score": round(sentiment_score, 3),
        "confidence": round(sentiment_score, 3)
    }

def main():
    print("🔍 Starting sentiment analysis on feedback data...")
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        feedback_collection = db[COLLECTION_NAME]
        
        print("✅ Connected to MongoDB")
        
        # Find unprocessed feedback
        unprocessed_feedback = feedback_collection.find({"processed": {"$ne": True}})
        unprocessed_list = list(unprocessed_feedback)
        
        print(f"📝 Found {len(unprocessed_list)} unprocessed feedback entries")
        
        if not unprocessed_list:
            print("🎉 No unprocessed feedback found!")
            return
        
        processed_count = 0
        for feedback in unprocessed_list:
            try:
                feedback_id = feedback["_id"]
                text = feedback.get("text", "")
                
                print(f"📝 Processing feedback: {feedback_id}")
                print(f"   Text: {text[:50]}...")
                
                # Perform sentiment analysis
                sentiment_result = simple_sentiment_analysis(text)
                
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
        
        # Generate summary statistics
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
        
        print("\n📊 Sentiment Analysis Summary:")
        print(f"Total processed: {summary['total_processed']}")
        print(f"Sentiment distribution: {summary['sentiment_distribution']}")
        print(f"Average scores: {summary['average_scores']}")
        
        # Close MongoDB connection
        client.close()
        print("✅ MongoDB connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 