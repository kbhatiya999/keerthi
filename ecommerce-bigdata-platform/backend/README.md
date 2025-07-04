# E-commerce BigData Platform Backend

A comprehensive e-commerce platform backend with JWT authentication, admin panel, and big data analytics integration.

## 🚀 Features

- **JWT Authentication** - Secure user authentication with role-based access
- **User Management** - Customer, Admin, and Super Admin roles
- **Product Management** - CRUD operations for products with categories
- **Order Management** - Complete order lifecycle with status tracking
- **Shopping Cart** - Session-based cart management
- **Event Tracking** - User behavior analytics and clickstream data
- **Big Data Integration** - Kafka event streaming for real-time analytics
- **Admin Dashboard** - Statistics and management interface
- **MongoDB** - NoSQL database for scalability
- **FastAPI** - Modern, fast web framework with automatic API documentation

## 📋 Prerequisites

- Python 3.8+
- MongoDB Atlas account
- Confluent Cloud account (for Kafka)
- Cloudinary account (for image uploads)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
cd ecommerce-bigdata-platform/backend
```

### 2. Bootstrap the Environment

```bash
./scripts/bootstrap.sh
```

This script will:
- Create virtual environment
- Install dependencies
- Initialize database
- Setup Kafka topics
- Run health checks

### 3. Configure Environment

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 4. Start the Server

```bash
./scripts/start.sh
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/bootstrap.sh` | One-time setup (env, deps, init) |
| `./scripts/start.sh` | Start the FastAPI server |
| `./scripts/setup-kafka.sh` | Create Kafka topics |
| `./scripts/health-check.sh` | Verify all services |

## 🔐 Authentication

### Default Admin Account
- **Email**: admin@ecommerce.com
- **Password**: admin123

### User Roles
- **customer** - Can browse products, place orders, manage cart
- **admin** - Can manage products, orders, view analytics
- **super_admin** - Full system access, user management

## 📚 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Products
- `GET /products` - List all products
- `POST /products` - Create product (admin only)
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product (admin only)
- `DELETE /products/{id}` - Delete product (admin only)

### Orders
- `POST /orders` - Create order
- `GET /orders` - List orders (user's own or all for admin)
- `GET /orders/{id}` - Get order details
- `PUT /orders/{id}` - Update order status (admin only)

### Cart
- `GET /cart` - Get user's cart
- `POST /cart/items` - Add item to cart
- `DELETE /cart/items/{product_id}` - Remove item from cart

### Admin
- `GET /admin/stats` - Platform statistics
- `GET /admin/recent-orders` - Recent orders
- `GET /users` - List all users (admin only)

### Events
- `POST /events` - Track user events

## 🗄️ Database Schema

### Collections
- `users` - User accounts and authentication
- `products` - Product catalog
- `orders` - Order management
- `carts` - Shopping carts
- `events` - User behavior tracking
- `categories` - Product categories
- `reviews` - Product reviews
- `wishlist` - User wishlists

## 📊 Big Data Integration

### Kafka Topics
- `ecommerce-user-events` - User registration, login, profile updates
- `ecommerce-orders` - Order creation, status changes
- `ecommerce-inventory` - Product changes, stock updates
- `ecommerce-clickstream` - User behavior, page views, searches
- `ecommerce-payments` - Payment events, success/failure

### Event Types
- User events: `user_registered`, `user_login`, `profile_updated`
- Order events: `order_created`, `order_updated`, `order_cancelled`
- Product events: `product_created`, `product_updated`, `product_deleted`
- Clickstream: `page_view`, `add_to_cart`, `search`, `view_product`
- Payment events: `payment_success`, `payment_failed`

## 🔍 Testing

### Using VSCode REST Client
1. Install the REST Client extension
2. Open `api.http`
3. Click "Send Request" above any endpoint
4. Replace placeholders with actual values

### Using curl
```bash
# Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 🚨 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URL` | MongoDB connection string | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka bootstrap servers | Yes |
| `KAFKA_API_KEY` | Kafka API key | Yes |
| `KAFKA_API_SECRET` | Kafka API secret | Yes |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | No |
| `CLOUDINARY_API_KEY` | Cloudinary API key | No |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | No |

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check your MongoDB Atlas connection string
   - Ensure IP whitelist includes your IP

2. **Kafka Topics Not Found**
   - Run `./scripts/setup-kafka.sh`
   - Check Confluent Cloud credentials

3. **JWT Token Issues**
   - Generate a new JWT secret key
   - Check token expiration settings

4. **Virtual Environment Issues**
   - Delete `venv/` and run `./scripts/bootstrap.sh` again

### Health Check
Run the health check script to diagnose issues:
```bash
./scripts/health-check.sh
```

## 📈 Monitoring

### Health Endpoints
- `GET /health` - Basic health check
- `GET /admin/stats` - Platform statistics (admin only)

### Logs
- Application logs are output to console
- Use `uvicorn main:app --log-level debug` for detailed logs

## 🔒 Security

- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Role-based access control
- Input validation with Pydantic
- CORS configuration for frontend integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 