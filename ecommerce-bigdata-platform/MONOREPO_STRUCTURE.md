# Monorepo Structure & Configuration Management

## 📁 **Project Structure**

```
ecommerce-bigdata-platform/
├── .env                          # Root shared configurations
├── backend/
│   ├── .env                      # Backend-specific configurations
│   ├── main.py                   # FastAPI application
│   ├── auth.py                   # Authentication logic
│   ├── database.py               # MongoDB connection
│   ├── kafka_config.py           # Kafka integration
│   └── scripts/                  # Backend utilities
├── cloud-services/
│   ├── .env                      # Cloud services configurations
│   ├── databricks/               # Databricks setup & config
│   ├── kafka/                    # Kafka setup & topics
│   ├── cloudinary/               # Cloudinary setup & config
│   ├── mongodb/                  # MongoDB setup
│   └── monitoring/               # Service monitoring scripts
├── frontend/
│   ├── .env                      # Frontend configurations
│   ├── src/                      # Next.js application
│   └── public/                   # Static assets
└── scripts/                      # Shared development scripts
```

## 🔧 **Configuration Management**

### **Root .env** (`/.env`)
- **Purpose**: Shared configurations across all modules
- **Contains**: Environment variables, ports, URLs, development settings
- **Used by**: All modules for common settings

### **Backend .env** (`/backend/.env`)
- **Purpose**: Backend application specific configurations
- **Contains**:
  - MongoDB connection settings
  - JWT authentication
  - Kafka integration (backend credentials)
  - Notification system settings
  - Server configuration

### **Cloud Services .env** (`/cloud-services/.env`)
- **Purpose**: Cloud service specific configurations
- **Contains**:
  - Databricks Community Edition credentials
  - Confluent Cloud Kafka credentials
  - Cloudinary API credentials
- **Used by**: All cloud service setup scripts

### **Frontend .env** (`/frontend/.env`)
- **Purpose**: Frontend application specific configurations
- **Contains**:
  - Next.js settings
  - API endpoints
  - Environment variables

## 🚀 **Module Independence**

Each module is designed to be **self-contained**:

### **Backend Module**
- Own database connections
- Own Kafka integration
- Own authentication system
- Can run independently

### **Cloud Services Module**
- Own cloud service credentials
- Own setup and monitoring scripts
- Can be deployed separately
- Manages external service connections

### **Frontend Module**
- Own API integrations
- Own build and deployment process
- Can run independently

## 📋 **Environment Variable Loading**

### **Backend Scripts**
```bash
# Load from backend/.env
source backend/.env
```

### **Cloud Services Scripts**
```bash
# Load from cloud-services/.env
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi
```

### **Root Scripts**
```bash
# Load from root .env
source .env
```

## 🔐 **Security Best Practices**

1. **Separate Credentials**: Each module has its own credentials
2. **No Cross-Module Dependencies**: Modules don't share sensitive data
3. **Environment-Specific**: Different .env files for different environments
4. **Git Ignore**: All .env files are in .gitignore

## 🛠 **Development Workflow**

### **Starting Backend**
```bash
cd backend
source .env
python main.py
```

### **Setting Up Cloud Services**
```bash
cd cloud-services
source .env
./setup-all-services.sh
```

### **Starting Frontend**
```bash
cd frontend
source .env
npm run dev
```

## 📊 **Configuration Hierarchy**

```
Root .env (Shared)
├── Backend .env (Backend-specific)
├── Cloud Services .env (Cloud-specific)
└── Frontend .env (Frontend-specific)
```

## 🔄 **Migration from Single .env**

If you previously had all configurations in one file:

1. **Backend configs** → `backend/.env`
2. **Cloud service configs** → `cloud-services/.env`
3. **Frontend configs** → `frontend/.env`
4. **Shared configs** → Root `.env`

## ✅ **Benefits of This Structure**

- **Modularity**: Each module is independent
- **Security**: Credentials are isolated
- **Scalability**: Easy to add new modules
- **Maintenance**: Clear separation of concerns
- **Deployment**: Can deploy modules separately
- **Development**: Teams can work independently 