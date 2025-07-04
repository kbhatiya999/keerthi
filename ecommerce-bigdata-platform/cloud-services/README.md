# Cloud Services Configuration

This directory contains all the cloud services configuration and setup scripts for the E-commerce Big Data Platform.

## 🚀 Quick Start

Run the comprehensive setup script to check all services:

```bash
./cloud-services/setup-all-services.sh
```

## 📋 Services Overview

### ✅ Configured Services

| Service | Status | Purpose | CLI Tool |
|---------|--------|---------|----------|
| **Cloudinary** | ✅ Working | Media management and CDN | `cloudinary` |
| **Databricks** | ✅ Working | Big data analytics | `databricks` |
| **MongoDB** | ✅ Working | Database | `mongosh` |
| **Kafka** | ✅ Working | Event streaming | `confluent` |

### ⚠️ Partially Configured Services

| Service | Status | Purpose | CLI Tool |
|---------|--------|---------|----------|
| *All services configured* | ✅ Complete | - | - |

## 🔧 Individual Service Setup

### 1. Cloudinary (Media Management)
```bash
# Setup
./cloud-services/cloudinary/setup.sh

# Test
./cloud-services/cloudinary/test-cli.sh

# Monitor
./cloud-services/monitoring/cloudinary-monitor.sh
```

**Features:**
- Image upload and transformation
- CDN delivery
- Automatic optimization
- Cloud storage

### 2. Databricks (Big Data Analytics)
```bash
# Setup
./cloud-services/databricks/setup.sh

# Test
./cloud-services/databricks/test-cli.sh

# Monitor
./cloud-services/monitoring/databricks-monitor.sh
```

**Features:**
- Community Edition (free)
- Spark clusters
- SQL warehouses
- Notebook environment
- Big data processing

### 3. MongoDB (Database)
```bash
# Setup
./cloud-services/mongodb/setup.sh

# Test
./cloud-services/mongodb/test-cli.sh

# Monitor
./cloud-services/monitoring/mongodb-monitor.sh
```

**Features:**
- Document database
- JSON-like data storage
- Scalable architecture
- Rich query language

### 4. Kafka (Event Streaming) - Needs Setup
```bash
# Setup (requires Confluent Cloud account)
./cloud-services/kafka/setup.sh

# Test
./cloud-services/kafka/test-kafka-events.sh

# Monitor
./cloud-services/monitoring/kafka-monitor.sh
```

**Features:**
- Real-time event streaming
- Message queuing
- Event sourcing
- Data pipeline integration

## 📊 Monitoring

All services have monitoring scripts that provide:
- Health checks
- Status reports
- Performance metrics
- Error diagnostics

Run all monitors:
```bash
./cloud-services/monitoring/*-monitor.sh
```

## 🔑 Environment Variables

Create a `.env` file in the project root with:

```env
# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Databricks
DATABRICKS_HOST=https://dbc-27febc87-68f1.cloud.databricks.com
DATABRICKS_TOKEN=your_token

# MongoDB
MONGODB_URI=mongodb://localhost:27017/ecommerce

# Kafka (when configured)
KAFKA_BOOTSTRAP_SERVERS=your_kafka_server
KAFKA_API_KEY=your_api_key
KAFKA_API_SECRET=your_api_secret
```

## 🧪 Testing

Each service has comprehensive test scripts:

```bash
# Test all services
./cloud-services/*/test-*.sh

# Test specific service
./cloud-services/databricks/test-cli.sh
./cloud-services/cloudinary/test-cli.sh
```

## 📁 Directory Structure

```
cloud-services/
├── cloudinary/           # Media management
├── databricks/           # Big data analytics
├── kafka/               # Event streaming
├── mongodb/             # Database
├── monitoring/          # Health monitoring scripts
├── setup-all-services.sh # Master setup script
└── README.md           # This file
```

## 🎯 Next Steps

1. **Complete Kafka Setup**: Sign up for Confluent Cloud and configure
2. **Environment Configuration**: Update `.env` file with all credentials
3. **Integration Testing**: Test service interactions
4. **Production Deployment**: Configure for production environment

## 🔗 Useful Links

- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [Databricks Community Edition](https://community.cloud.databricks.com)
- [MongoDB Documentation](https://docs.mongodb.com)
- [Confluent Cloud](https://www.confluent.io/confluent-cloud/)

## 🆘 Troubleshooting

### Common Issues

1. **CLI not found**: Install the required CLI tools
2. **Authentication failed**: Check credentials and tokens
3. **Connection timeout**: Verify network connectivity
4. **Permission denied**: Check file permissions on scripts

### Getting Help

1. Check individual service logs
2. Run monitoring scripts for diagnostics
3. Verify environment variables
4. Test individual components

---

**Last Updated**: June 30, 2025
**Status**: 4/4 services fully configured 