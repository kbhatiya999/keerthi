from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Product(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int
    image_url: Optional[str] = None

class Customer(BaseModel):
    clerk_user_id: str
    email: str
    name: str
    created_at: datetime = datetime.utcnow()

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class Order(BaseModel):
    customer_id: str
    items: List[OrderItem]
    total_amount: float
    status: str = "pending"
    created_at: datetime = datetime.utcnow()
    channel: str = "website"  # website, mobile, in-store

class Event(BaseModel):
    event_type: str  # page_view, add_to_cart, purchase, etc.
    customer_id: Optional[str]
    product_id: Optional[str]
    session_id: str
    timestamp: datetime = datetime.utcnow()
    properties: dict = {}

