from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# Base models
class Product(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int
    image_url: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    tags: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class User(BaseModel):
    email: str
    name: str
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: UserRole = UserRole.CUSTOMER

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float
    product_name: Optional[str] = None

class Order(BaseModel):
    customer_id: str
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    shipping_address: Dict[str, Any] = {}
    billing_address: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    channel: str = "website"  # website, mobile, in-store

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None

class Event(BaseModel):
    event_type: str  # page_view, add_to_cart, purchase, etc.
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    properties: Dict[str, Any] = {}

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Cart(BaseModel):
    customer_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Category(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Review(BaseModel):
    product_id: str
    customer_id: str
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WishlistItem(BaseModel):
    customer_id: str
    product_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Response models
class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int
    image_url: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    tags: List[str] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

class OrderResponse(BaseModel):
    id: str
    customer_id: str
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    shipping_address: Dict[str, Any]
    billing_address: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    channel: str

