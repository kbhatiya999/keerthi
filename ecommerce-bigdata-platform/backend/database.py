import motor.motor_asyncio
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ecommerce_bigdata")

# Create async client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Collections
users_collection = db.users
products_collection = db.products
orders_collection = db.orders
events_collection = db.events
carts_collection = db.carts
categories_collection = db.categories
reviews_collection = db.reviews
wishlist_collection = db.wishlist
feedback_collection = db.feedback

async def create_indexes():
    """Create database indexes for optimal performance"""
    
    # Users collection indexes
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("role")
    await users_collection.create_index("is_active")
    
    # Products collection indexes
    await products_collection.create_index("category")
    await products_collection.create_index("brand")
    await products_collection.create_index("is_active")
    await products_collection.create_index("sku", unique=True, sparse=True)
    await products_collection.create_index("tags")
    await products_collection.create_index([("name", "text"), ("description", "text")])
    
    # Orders collection indexes
    await orders_collection.create_index("customer_id")
    await orders_collection.create_index("status")
    await orders_collection.create_index("payment_status")
    await orders_collection.create_index("created_at")
    await orders_collection.create_index("channel")
    
    # Events collection indexes
    await events_collection.create_index("customer_id")
    await events_collection.create_index("event_type")
    await events_collection.create_index("timestamp")
    await events_collection.create_index("session_id")
    
    # Carts collection indexes
    await carts_collection.create_index("customer_id", unique=True)
    await carts_collection.create_index("updated_at")
    
    # Categories collection indexes
    await categories_collection.create_index("parent_id")
    await categories_collection.create_index("is_active")
    await categories_collection.create_index("name")
    
    # Reviews collection indexes
    await reviews_collection.create_index("product_id")
    await reviews_collection.create_index("customer_id")
    await reviews_collection.create_index("rating")
    await reviews_collection.create_index("created_at")
    
    # Wishlist collection indexes
    await wishlist_collection.create_index([("customer_id", 1), ("product_id", 1)], unique=True)
    await wishlist_collection.create_index("customer_id")
    
    # Feedback collection indexes
    await feedback_collection.create_index("user_id")
    await feedback_collection.create_index("product_id")
    await feedback_collection.create_index("feedback_type")
    await feedback_collection.create_index("created_at")
    await feedback_collection.create_index("processed")
    await feedback_collection.create_index([("text", "text")])  # Text search index

async def init_database():
    """Initialize database with default data"""
    
    # Create indexes
    await create_indexes()
    
    # Create default super admin if not exists
    from auth import get_password_hash
    
    super_admin = await users_collection.find_one({"email": "admin@ecommerce.com"})
    if not super_admin:
        admin_data = {
            "email": "admin@ecommerce.com",
            "name": "Super Admin",
            "password_hash": get_password_hash("admin123"),
            "role": "super_admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await users_collection.insert_one(admin_data)
        print("✅ Super admin created: admin@ecommerce.com / admin123")
    
    # Create default categories
    default_categories = [
        {"name": "Electronics", "description": "Electronic devices and gadgets"},
        {"name": "Clothing", "description": "Fashion and apparel"},
        {"name": "Books", "description": "Books and publications"},
        {"name": "Home & Garden", "description": "Home improvement and garden supplies"},
        {"name": "Sports", "description": "Sports equipment and accessories"}
    ]
    
    for category in default_categories:
        existing = await categories_collection.find_one({"name": category["name"]})
        if not existing:
            category["is_active"] = True
            category["created_at"] = datetime.utcnow()
            await categories_collection.insert_one(category)
    
    print("✅ Database initialized successfully")

# Initialize MongoDB connection with error handling
try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    database = client.ecommerce_db
    
    # Collections
    products_collection = database.get_collection("products")
    customers_collection = database.get_collection("customers") 
    orders_collection = database.get_collection("orders")
    events_collection = database.get_collection("events")
    
    logger.info("✅ MongoDB connected successfully")
    
except Exception as e:
    logger.warning(f"⚠️ MongoDB connection failed: {e}")
    logger.info("📝 Running in demo mode without MongoDB persistence")
    
    # Create mock collections for demo mode
    class MockCollection:
        async def insert_one(self, data):
            logger.info(f"📝 Mock insert: {data}")
            return type('MockResult', (), {'inserted_id': 'mock_id'})()
        
        async def find(self):
            # Return empty list for demo
            return []
    
    products_collection = MockCollection()
    customers_collection = MockCollection()
    orders_collection = MockCollection()
    events_collection = MockCollection()

