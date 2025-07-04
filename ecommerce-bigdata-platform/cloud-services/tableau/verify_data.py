#!/usr/bin/env python3
"""
Verify MongoDB data is ready for Tableau dashboard
"""

import pymongo
from datetime import datetime
import json

# Configuration
MONGODB_URL = "mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "ecommerce"
COLLECTION_NAME = "feedback"

def main():
    print("🔍 Verifying MongoDB data for Tableau dashboard...")
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        feedback_collection = db[COLLECTION_NAME]
        
        print("✅ Connected to MongoDB")
        
        # Get all feedback data
        all_feedback = list(feedback_collection.find())
        
        print(f"📊 Total feedback entries: {len(all_feedback)}")
        
        if not all_feedback:
            print("❌ No feedback data found!")
            return
        
        # Check processed vs unprocessed
        processed = [f for f in all_feedback if f.get("processed", False)]
        unprocessed = [f for f in all_feedback if not f.get("processed", False)]
        
        print(f"✅ Processed feedback: {len(processed)}")
        print(f"⏳ Unprocessed feedback: {len(unprocessed)}")
        
        # Show sample processed data
        if processed:
            print("\n📋 Sample processed feedback:")
            for i, feedback in enumerate(processed[:3]):
                print(f"  {i+1}. ID: {feedback['_id']}")
                print(f"     Text: {feedback.get('text', '')[:50]}...")
                print(f"     Sentiment: {feedback.get('sentiment_label', 'N/A')}")
                print(f"     Score: {feedback.get('sentiment_score', 'N/A')}")
                print(f"     Type: {feedback.get('feedback_type', 'N/A')}")
                print(f"     Category: {feedback.get('category', 'N/A')}")
                print(f"     Rating: {feedback.get('rating', 'N/A')}")
                print(f"     Created: {feedback.get('created_at', 'N/A')}")
                print()
        
        # Generate summary statistics
        pipeline = [
            {"$match": {"processed": True}},
            {"$group": {
                "_id": "$sentiment_label",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$sentiment_score"},
                "avg_rating": {"$avg": "$rating"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(feedback_collection.aggregate(pipeline))
        
        print("📈 Sentiment Analysis Summary:")
        for result in results:
            sentiment = result["_id"]
            count = result["count"]
            avg_score = result["avg_score"]
            avg_rating = result["avg_rating"]
            print(f"  {sentiment.capitalize()}: {count} entries, avg score: {avg_score:.3f}, avg rating: {avg_rating:.1f}")
        
        # Category breakdown
        category_pipeline = [
            {"$match": {"processed": True}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "avg_sentiment": {"$avg": "$sentiment_score"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        category_results = list(feedback_collection.aggregate(category_pipeline))
        
        print("\n🏷️ Category Breakdown:")
        for result in category_results:
            category = result["_id"]
            count = result["count"]
            avg_sentiment = result["avg_sentiment"]
            print(f"  {category.capitalize()}: {count} entries, avg sentiment: {avg_sentiment:.3f}")
        
        # Feedback type breakdown
        type_pipeline = [
            {"$match": {"processed": True}},
            {"$group": {
                "_id": "$feedback_type",
                "count": {"$sum": 1},
                "avg_sentiment": {"$avg": "$sentiment_score"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        type_results = list(feedback_collection.aggregate(type_pipeline))
        
        print("\n📝 Feedback Type Breakdown:")
        for result in type_results:
            feedback_type = result["_id"]
            count = result["count"]
            avg_sentiment = result["avg_sentiment"]
            print(f"  {feedback_type.capitalize()}: {count} entries, avg sentiment: {avg_sentiment:.3f}")
        
        print("\n✅ Data is ready for Tableau!")
        print("\n📋 Tableau Connection Details:")
        print(f"  Server: cluster0.tbyigvr.mongodb.net")
        print(f"  Database: {DATABASE_NAME}")
        print(f"  Collection: {COLLECTION_NAME}")
        print(f"  Username: root")
        print(f"  Password: root")
        
        print("\n🎯 Key Fields for Visualization:")
        print("  - sentiment_label (positive/negative/neutral)")
        print("  - sentiment_score (0-1)")
        print("  - confidence (0-1)")
        print("  - created_at (timestamp)")
        print("  - processed_at (analysis timestamp)")
        print("  - feedback_type (product/service/delivery)")
        print("  - category (electronics/clothing/etc)")
        print("  - rating (1-5 stars)")
        print("  - text (feedback content)")
        
        # Close MongoDB connection
        client.close()
        print("\n✅ MongoDB connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 