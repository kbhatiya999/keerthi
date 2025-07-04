#!/bin/bash

echo "📊 Setting up Kafka Topics for Sentiment Analysis"
echo "================================================="

CLUSTER_ID="lkc-dxp5o1"

# Create sentiment analysis topic
echo "📝 Creating sentiment analysis topic..."
confluent kafka topic create ecommerce-sentiment-analysis --partitions 3 --replication-factor 3

# Create sentiment summary topic
echo "📝 Creating sentiment summary topic..."
confluent kafka topic create ecommerce-sentiment-summary --partitions 3 --replication-factor 3

# Create sentiment alerts topic
echo "📝 Creating sentiment alerts topic..."
confluent kafka topic create ecommerce-sentiment-alerts --partitions 3 --replication-factor 3

# Create raw feedback topic for Databricks processing
echo "📝 Creating raw feedback topic..."
confluent kafka topic create ecommerce-feedback-raw --partitions 3 --replication-factor 3

echo ""
echo "✅ Sentiment Analysis Topics Created:"
echo "  - ecommerce-sentiment-analysis"
echo "  - ecommerce-sentiment-summary" 
echo "  - ecommerce-sentiment-alerts"
echo "  - ecommerce-feedback-raw"
echo ""
echo "📊 Topics can be monitored with:"
echo "  confluent kafka topic consume ecommerce-sentiment-analysis --from-beginning" 