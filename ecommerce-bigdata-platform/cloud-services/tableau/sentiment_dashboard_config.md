# Tableau Sentiment Analysis Dashboard Configuration

## Overview
This document outlines the setup and configuration for the Tableau dashboard that visualizes customer feedback sentiment analysis results.

## Data Sources

### 1. MongoDB Connection
- **Connection Type**: MongoDB Atlas
- **Connection String**: `mongodb+srv://root:root@cluster0.tbyigvr.mongodb.net/ecommerce`
- **Collection**: `feedback`

### 2. Kafka Stream (Real-time)
- **Connection Type**: Kafka Stream
- **Bootstrap Servers**: `pkc-921jm.us-east-2.aws.confluent.cloud:9092`
- **Topics**: 
  - `ecommerce-sentiment-analysis` (processed results)
  - `ecommerce-sentiment-summary` (summary statistics)

## Dashboard Components

### 1. Real-time Sentiment Overview
- **Chart Type**: Gauge Chart
- **Metrics**:
  - Overall Sentiment Score (0-1)
  - Positive Feedback Percentage
  - Negative Feedback Percentage
  - Neutral Feedback Percentage

### 2. Sentiment Distribution
- **Chart Type**: Pie Chart
- **Dimensions**: Sentiment Label (Positive/Negative/Neutral)
- **Measures**: Count of feedback

### 3. Sentiment Trends Over Time
- **Chart Type**: Line Chart
- **Dimensions**: Date (processed_at)
- **Measures**: 
  - Average Sentiment Score
  - Count of feedback by sentiment

### 4. Product Performance
- **Chart Type**: Bar Chart
- **Dimensions**: Product ID/Name
- **Measures**: 
  - Average Sentiment Score
  - Total Feedback Count
  - Positive Feedback Percentage

### 5. Keyword Analysis
- **Chart Type**: Word Cloud
- **Dimensions**: Keywords (extracted from feedback)
- **Measures**: Frequency count

### 6. Feedback Source Analysis
- **Chart Type**: Horizontal Bar Chart
- **Dimensions**: Source (website, mobile, email, chat)
- **Measures**: 
  - Sentiment distribution
  - Average rating

## Calculated Fields

### 1. Sentiment Score Category
```sql
CASE 
  WHEN [sentiment_score] >= 0.7 THEN "Very Positive"
  WHEN [sentiment_score] >= 0.5 THEN "Positive"
  WHEN [sentiment_score] >= 0.3 THEN "Neutral"
  WHEN [sentiment_score] >= 0.1 THEN "Negative"
  ELSE "Very Negative"
END
```

### 2. Response Time (if applicable)
```sql
DATEDIFF('hour', [created_at], [processed_at])
```

### 3. Sentiment Trend
```sql
// Moving average of sentiment scores
WINDOW_AVG([sentiment_score], -7, 0)
```

## Filters

### 1. Date Range Filter
- **Type**: Date Range
- **Field**: processed_at
- **Default**: Last 30 days

### 2. Sentiment Filter
- **Type**: Multiple Selection
- **Field**: sentiment_label
- **Options**: Positive, Negative, Neutral

### 3. Product Filter
- **Type**: Dropdown
- **Field**: product_id
- **Source**: Products collection

### 4. Feedback Type Filter
- **Type**: Multiple Selection
- **Field**: feedback_type
- **Options**: review, survey, chat, support_ticket

## Alerts and Notifications

### 1. Negative Sentiment Alert
- **Condition**: Sentiment Score < 0.3
- **Threshold**: 10% of total feedback
- **Action**: Email notification to customer service team

### 2. Product Performance Alert
- **Condition**: Average sentiment score < 0.4
- **Threshold**: 5 feedback in last 24 hours
- **Action**: Dashboard highlight and notification

### 3. Response Time Alert
- **Condition**: Processing time > 2 hours
- **Action**: Technical team notification

## Dashboard Layout

### Header Section
- Company logo
- Last updated timestamp
- Refresh button
- Export options

### Main Content (3x2 Grid)
1. **Top Row**:
   - Sentiment Overview Gauge
   - Sentiment Distribution Pie Chart
   - Real-time Feedback Counter

2. **Middle Row**:
   - Sentiment Trends Line Chart
   - Product Performance Bar Chart
   - Keyword Analysis Word Cloud

3. **Bottom Row**:
   - Feedback Source Analysis
   - Recent Feedback Table
   - Performance Metrics

### Sidebar Filters
- Date Range
- Sentiment Type
- Product Selection
- Feedback Type
- Source Filter

## Data Refresh Schedule

### Real-time Data
- **Kafka Stream**: Every 30 seconds
- **MongoDB**: Every 5 minutes

### Batch Processing
- **Daily Summary**: 2:00 AM UTC
- **Weekly Report**: Every Monday 6:00 AM UTC
- **Monthly Analytics**: First day of month 8:00 AM UTC

## Performance Optimization

### 1. Data Aggregation
- Pre-aggregate daily sentiment scores
- Create materialized views for common queries
- Index frequently queried fields

### 2. Caching Strategy
- Cache static data (products, categories)
- Implement query result caching
- Use incremental refresh for large datasets

### 3. Connection Pooling
- Configure MongoDB connection pool
- Optimize Kafka consumer settings
- Monitor connection health

## Security Considerations

### 1. Data Access
- Role-based access control
- Encrypt sensitive feedback data
- Audit log for dashboard access

### 2. API Security
- Secure MongoDB connection
- Kafka authentication
- API rate limiting

## Monitoring and Maintenance

### 1. Dashboard Health
- Monitor data refresh status
- Track query performance
- Alert on data quality issues

### 2. User Analytics
- Track dashboard usage
- Monitor user engagement
- Gather feedback on dashboard usability

## Integration Points

### 1. Customer Service Integration
- Direct link to feedback details
- Integration with ticketing system
- Automated alert routing

### 2. Product Management
- Product performance insights
- Feature request tracking
- Quality improvement recommendations

### 3. Marketing Integration
- Customer satisfaction metrics
- Brand sentiment tracking
- Campaign effectiveness analysis

## Troubleshooting

### Common Issues
1. **Data not refreshing**: Check Kafka connection and MongoDB connectivity
2. **Slow performance**: Optimize queries and check data volume
3. **Missing data**: Verify data pipeline and processing status

### Support Contacts
- **Technical Issues**: Databricks team
- **Data Issues**: Data engineering team
- **Dashboard Issues**: BI team 