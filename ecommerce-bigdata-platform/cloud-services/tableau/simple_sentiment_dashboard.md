# Simple Sentiment Analysis Dashboard - Tableau

## 🎯 Super Simple Architecture
**MongoDB → Databricks → MongoDB (with results) → Tableau**

No Kafka needed! Just direct MongoDB connections.

## 📊 Dashboard Overview

### **Data Source**
- **Connection**: MongoDB Atlas
- **Database**: `ecommerce`
- **Collection**: `feedback`

### **Key Metrics to Visualize**

#### 1. **Sentiment Overview**
- Total feedback count
- Sentiment distribution (positive/negative/neutral)
- Average sentiment scores
- Processing status (processed vs unprocessed)

#### 2. **Time-based Analysis**
- Sentiment trends over time
- Daily/weekly/monthly sentiment patterns
- Peak feedback periods

#### 3. **Category Analysis**
- Sentiment by feedback type (product, service, delivery, etc.)
- Sentiment by product category
- Top positive/negative categories

#### 4. **Customer Insights**
- Sentiment by customer rating (1-5 stars)
- High-value customer sentiment
- Customer satisfaction trends

## 🎨 Dashboard Components

### **Main Dashboard**
```
┌─────────────────────────────────────────────────────────────┐
│                    Customer Sentiment Dashboard              │
├─────────────────────────────────────────────────────────────┤
│  📊 Sentiment Overview  │  📈 Trends  │  🏷️ Categories     │
│  • Positive: 65%        │  • Time     │  • Product: 45%    │
│  • Negative: 20%        │  • Sentiment│  • Service: 30%    │
│  • Neutral: 15%         │  • Volume   │  • Delivery: 25%   │
├─────────────────────────────────────────────────────────────┤
│  📋 Recent Feedback     │  🎯 Key Insights                  │
│  • Latest entries       │  • Top concerns                  │
│  • Sentiment labels     │  • Improvement areas             │
│  • Processing status    │  • Success stories               │
└─────────────────────────────────────────────────────────────┘
```

### **Detailed Views**

#### **1. Sentiment Distribution Chart**
- **Type**: Pie chart or donut chart
- **Data**: `sentiment_label` count
- **Colors**: Green (positive), Red (negative), Gray (neutral)

#### **2. Sentiment Trends**
- **Type**: Line chart
- **X-axis**: `created_at` (date)
- **Y-axis**: Average `sentiment_score`
- **Filters**: Date range, feedback type

#### **3. Category Performance**
- **Type**: Horizontal bar chart
- **X-axis**: Average sentiment score
- **Y-axis**: `category` or `feedback_type`
- **Color**: Sentiment label

#### **4. Feedback Volume Timeline**
- **Type**: Area chart
- **X-axis**: `created_at` (date)
- **Y-axis**: Count of feedback
- **Color**: `sentiment_label`

## 🔧 Setup Instructions

### **1. Connect to MongoDB Atlas**
```
1. Open Tableau Desktop
2. Connect → To a Server → MongoDB
3. Server: cluster0.tbyigvr.mongodb.net
4. Database: ecommerce
5. Authentication: Username/Password
   - Username: root
   - Password: root
```

### **2. Create Data Source**
```
1. Select 'feedback' collection
2. Preview data to ensure connection
3. Verify key fields:
   - sentiment_label
   - sentiment_score
   - confidence
   - created_at
   - processed_at
   - feedback_type
   - category
   - product_id
```

### **3. Build Worksheets**

#### **Worksheet 1: Sentiment Overview**
```
- Calculated Field: Sentiment Count
- Chart: Pie chart
- Dimensions: sentiment_label
- Measures: COUNT(*)
```

#### **Worksheet 2: Time Trends**
```
- Chart: Line chart
- Dimensions: DATE(created_at)
- Measures: AVG(sentiment_score)
- Filters: Date range
```

#### **Worksheet 3: Category Analysis**
```
- Chart: Horizontal bar chart
- Dimensions: category
- Measures: AVG(sentiment_score)
- Color: sentiment_label
```

### **4. Create Dashboard**
```
1. Combine all worksheets
2. Add filters:
   - Date range
   - Sentiment label
   - Category
   - Feedback type
3. Add title and descriptions
4. Set refresh schedule
```

## 📈 Key Performance Indicators (KPIs)

### **Customer Satisfaction Metrics**
- **Overall Sentiment Score**: Average sentiment across all feedback
- **Positive Feedback Rate**: % of positive feedback
- **Negative Feedback Rate**: % of negative feedback
- **Processing Rate**: % of feedback processed by Databricks

### **Trend Metrics**
- **Sentiment Trend**: 7-day moving average
- **Volume Trend**: Daily feedback volume
- **Category Performance**: Sentiment by category over time

### **Alert Thresholds**
- **Negative Feedback Spike**: >25% negative in 24 hours
- **Low Processing Rate**: <90% processed in 24 hours
- **Category Issues**: <0.3 sentiment score for any category

## 🔄 Refresh Strategy

### **Manual Refresh**
- Run Databricks notebook when needed
- Refresh Tableau dashboard after processing

### **Automated Refresh** (Future)
- Schedule Databricks notebook to run daily
- Set Tableau to refresh every 4 hours
- Email alerts for threshold breaches

## 📱 Mobile Optimization

### **Responsive Design**
- Optimize charts for mobile viewing
- Use simplified views for small screens
- Focus on key metrics on mobile

### **Mobile Dashboard**
```
┌─────────────────┐
│ Sentiment Score │
│     7.2/10      │
├─────────────────┤
│ Positive: 65%   │
│ Negative: 20%   │
│ Neutral: 15%    │
└─────────────────┘
```

## 🎯 Success Metrics

### **Dashboard Adoption**
- Daily active users
- Time spent on dashboard
- User feedback on usefulness

### **Business Impact**
- Response time to negative feedback
- Customer satisfaction improvement
- Product/service improvements based on insights

---

## 🚀 Next Steps

1. **Set up MongoDB connection** in Tableau
2. **Create initial worksheets** with sample data
3. **Build dashboard** with key metrics
4. **Test with real data** from Databricks processing
5. **Iterate and improve** based on user feedback

This simple approach eliminates Kafka complexity while still providing powerful sentiment analysis insights! 🎉 