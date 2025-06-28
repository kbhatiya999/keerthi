import motor.motor_asyncio
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
database = client.ecommerce_db

# Collections
products_collection = database.get_collection("products")
customers_collection = database.get_collection("customers") 
orders_collection = database.get_collection("orders")
events_collection = database.get_collection("events")

