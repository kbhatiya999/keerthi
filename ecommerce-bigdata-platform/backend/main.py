from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from datetime import datetime, timedelta
from typing import List, Optional
import os
from dotenv import load_dotenv
import uuid
from bson import ObjectId

# Import our modules
from auth import (
    User, UserCreate, UserLogin, Token, 
    create_access_token, verify_password, get_password_hash,
    get_current_active_user, get_current_admin_user, get_current_super_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import (
    Product, ProductUpdate, ProductResponse, Order, OrderUpdate, OrderResponse,
    Event, Cart, CartItem, Category, Review, WishlistItem,
    UserRole, OrderStatus, PaymentStatus, UserResponse
)
from database import (
    users_collection, products_collection, orders_collection, events_collection,
    carts_collection, categories_collection, reviews_collection, wishlist_collection,
    feedback_collection, init_database
)
from kafka_config import (
    get_kafka_producer, send_kafka_event, TOPICS,
    send_fraud_event, send_stock_alert, send_order_tracking_event, send_notification_event
)
from notifications import notification_service
from realtime_analytics import realtime_analytics



load_dotenv()

app = FastAPI(
    title="E-commerce BigData Platform API",
    description="Complete e-commerce platform with JWT authentication, admin panel, and big data analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Kafka producer
kafka_producer = get_kafka_producer()





# Startup event
@app.on_event("startup")
async def startup_event():
    await init_database()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# ==================== AUTHENTICATION ROUTES ====================

@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_dict = user_data.dict()
    user_dict["password_hash"] = get_password_hash(user_data.password)
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["is_active"] = True  # Ensure is_active is set
    del user_dict["password"]
    
    result = await users_collection.insert_one(user_dict)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data.email, "role": user_data.role},
        expires_delta=access_token_expires
    )
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['USER_EVENTS'],
        f"user_{result.inserted_id}",
        {
            "event_type": "user_registered",
            "user_id": str(result.inserted_id),
            "email": user_data.email,
            "role": user_data.role
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(result.inserted_id),
        "email": user_data.email,
        "role": user_data.role
    }

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    # Find user
    user = await users_collection.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['USER_EVENTS'],
        f"user_{user['_id']}",
        {
            "event_type": "user_login",
            "user_id": str(user["_id"]),
            "email": user["email"]
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    }

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user

# ==================== USER MANAGEMENT ROUTES ====================

@app.post("/users", response_model=dict)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_super_admin_user)
):
    """Create a new user (Super Admin only)"""
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Super admin can create admin users, but regular admins cannot
    if user_data.role == "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create super admin users"
        )
    
    # Create new user
    user_dict = user_data.dict()
    user_dict["password_hash"] = get_password_hash(user_data.password)
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["is_active"] = True  # Ensure is_active is set
    del user_dict["password"]
    
    result = await users_collection.insert_one(user_dict)
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['USER_EVENTS'],
        f"user_{result.inserted_id}",
        {
            "event_type": "user_created_by_admin",
            "user_id": str(result.inserted_id),
            "email": user_data.email,
            "role": user_data.role,
            "created_by": current_user.id
        }
    )
    
    return {"id": str(result.inserted_id), "message": "User created successfully"}

@app.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Get users (Admin and Super Admin only)"""
    filter_query = {}
    if role:
        filter_query["role"] = role
    
    # Regular admins can only see customers, super admins can see all
    if current_user.role == "admin":
        filter_query["role"] = "customer"
    
    users = []
    cursor = users_collection.find(filter_query).skip(skip).limit(limit)
    async for user in cursor:
        # Ensure all required fields are present with defaults
        user_data = {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "is_active": user.get("is_active", True),  # Default to True if missing
            "created_at": user.get("created_at", datetime.utcnow()),
            "updated_at": user.get("updated_at", datetime.utcnow())
        }
        users.append(UserResponse(**user_data))
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get specific user (Admin and Super Admin only)"""
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Regular admins can only access customer data
    if current_user.role == "admin" and user["role"] != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    
    # Ensure all required fields are present with defaults
    user_data = {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "is_active": user.get("is_active", True),  # Default to True if missing
        "created_at": user.get("created_at", datetime.utcnow()),
        "updated_at": user.get("updated_at", datetime.utcnow())
    }
    return UserResponse(**user_data)

@app.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: dict,
    current_user: User = Depends(get_current_admin_user)
):
    """Update user (Admin and Super Admin only)"""
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Regular admins can only update customers
    if current_user.role == "admin" and user["role"] != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Super admins can update any user except other super admins
    if current_user.role == "super_admin" and user["role"] == "super_admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other super admin users"
        )
    
    # Prevent role escalation
    if "role" in user_update:
        if current_user.role == "admin" and user_update["role"] != "customer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only assign customer role"
            )
        if user_update["role"] == "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot assign super admin role"
            )
    
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {**user_update, "updated_at": datetime.utcnow()}}
    )
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['USER_EVENTS'],
        f"user_{user_id}",
        {
            "event_type": "user_updated",
            "user_id": user_id,
            "updated_by": current_user.id,
            "updates": user_update
        }
    )
    
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_super_admin_user)
):
    """Delete user (Super Admin only)"""
    # Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Get the user to check their role
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Cannot delete other super admins
    if user["role"] == "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete super admin users"
        )
    
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['USER_EVENTS'],
        f"user_{user_id}",
        {
            "event_type": "user_deleted",
            "user_id": user_id,
            "deleted_by": current_user.id
        }
    )
    
    return {"message": "User deleted successfully"}

# ==================== PRODUCT ROUTES ====================

@app.post("/products", response_model=dict)
async def create_product(
    product: Product,
    current_user: User = Depends(get_current_admin_user)
):
    product_dict = product.dict()
    
    # Generate unique SKU if not provided
    if not product_dict.get("sku"):
        product_dict["sku"] = f"SKU-{uuid.uuid4().hex[:8].upper()}"
    
    try:
        result = await products_collection.insert_one(product_dict)
        
        # Send Kafka event
        product_dict["_id"] = str(result.inserted_id)
        send_kafka_event(
            kafka_producer,
            TOPICS['INVENTORY'],
            f"product_{result.inserted_id}",
            {
                "event_type": "product_created",
                "product": product_dict
            }
        )
        
        return {"id": str(result.inserted_id)}
    except Exception as e:
        if "duplicate key error" in str(e) and "sku" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_dict.get('sku')}' already exists. Please use a different SKU."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create product"
            )

@app.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    filter_query = {"is_active": True}
    if category:
        filter_query["category"] = category
    if search:
        filter_query["$text"] = {"$search": search}
    
    products = []
    cursor = products_collection.find(filter_query).skip(skip).limit(limit)
    async for product in cursor:
        product["id"] = str(product["_id"])
        products.append(ProductResponse(**product))
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product["id"] = str(product["_id"])
    return ProductResponse(**product)

@app.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    update_data = {k: v for k, v in product_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['INVENTORY'],
        f"product_{product_id}",
        {
            "event_type": "product_updated",
            "product_id": product_id,
            "updates": update_data
        }
    )
    
    return {"message": "Product updated successfully"}

@app.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['INVENTORY'],
        f"product_{product_id}",
        {
            "event_type": "product_deleted",
            "product_id": product_id
        }
    )
    
    return {"message": "Product deleted successfully"}

# ==================== ORDER ROUTES ====================

@app.post("/orders", response_model=dict)
async def create_order(
    order: Order,
    current_user: User = Depends(get_current_active_user)
):
    # Verify order belongs to current user (unless admin)
    if current_user.role == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order_dict = order.dict()
    result = await orders_collection.insert_one(order_dict)
    
    # Send Kafka event
    order_dict["_id"] = str(result.inserted_id)
    send_kafka_event(
        kafka_producer,
        TOPICS['ORDERS'],
        f"order_{result.inserted_id}",
        {
            "event_type": "order_created",
            "order": order_dict
        }
    )
    
    return {"order_id": str(result.inserted_id)}

@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    # Customers can only see their own orders
    filter_query = {}
    if current_user.role == "customer":
        filter_query["customer_id"] = current_user.id
    
    orders = []
    cursor = orders_collection.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
    async for order in cursor:
        # Ensure all required fields are present with defaults
        order["id"] = str(order["_id"])
        order.setdefault("status", "pending")
        order.setdefault("payment_status", "pending")
        order.setdefault("created_at", datetime.utcnow())
        order.setdefault("updated_at", datetime.utcnow())
        order.setdefault("channel", "website")
        
        # Fix: Coerce shipping_address and billing_address to dict if not already
        sa = order.get("shipping_address", {})
        if isinstance(sa, dict):
            order["shipping_address"] = sa
        elif isinstance(sa, str):
            order["shipping_address"] = {"address": sa}
        else:
            order["shipping_address"] = {}
            
        ba = order.get("billing_address", {})
        if isinstance(ba, dict):
            order["billing_address"] = ba
        elif isinstance(ba, str):
            order["billing_address"] = {"address": ba}
        else:
            order["billing_address"] = {}
            
        orders.append(OrderResponse(**order))
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user)
):
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization
    if current_user.role == "customer" and order["customer_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Ensure all required fields are present with defaults
    order["id"] = str(order["_id"])
    order.setdefault("status", "pending")
    order.setdefault("payment_status", "pending")
    order.setdefault("created_at", datetime.utcnow())
    order.setdefault("updated_at", datetime.utcnow())
    order.setdefault("channel", "website")
    
    # Fix: Coerce shipping_address and billing_address to dict if not already
    sa = order.get("shipping_address", {})
    if isinstance(sa, dict):
        order["shipping_address"] = sa
    elif isinstance(sa, str):
        order["shipping_address"] = {"address": sa}
    else:
        order["shipping_address"] = {}
    
    ba = order.get("billing_address", {})
    if isinstance(ba, dict):
        order["billing_address"] = ba
    elif isinstance(ba, str):
        order["billing_address"] = {"address": ba}
    else:
        order["billing_address"] = {}
    
    return OrderResponse(**order)

@app.put("/orders/{order_id}")
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    # Get current order to track status changes
    current_order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not current_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = current_order.get("status", "pending")
    customer_id = current_order.get("customer_id")
    total_amount = current_order.get("total_amount", 0)
    
    update_data = {k: v for k, v in order_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Real-time order tracking
    new_status = update_data.get("status", old_status)
    if new_status != old_status:
        # Track order status change
        tracking_data = realtime_analytics.track_order_status(
            order_id, new_status, customer_id, total_amount
        )
        
        # Send order tracking event to Kafka
        send_order_tracking_event(kafka_producer, tracking_data)
        
        # Send notification to customer
        if customer_id:
            customer = await users_collection.find_one({"_id": ObjectId(customer_id)})
            if customer:
                notification_service.notify_order_status_change(
                    order_id, customer["email"], old_status, new_status, current_order
                )
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['ORDERS'],
        f"order_{order_id}",
        {
            "event_type": "order_updated",
            "order_id": order_id,
            "updates": update_data
        }
    )
    
    return {"message": "Order updated successfully"}

@app.delete("/orders/{order_id}")
async def delete_order(
    order_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Delete an order (Admin only)"""
    # Check if order exists
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Delete the order
    result = await orders_collection.delete_one({"_id": ObjectId(order_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['ORDERS'],
        f"order_{order_id}",
        {
            "event_type": "order_deleted",
            "order_id": order_id,
            "customer_id": order.get("customer_id"),
            "total_amount": order.get("total_amount")
        }
    )
    
    return {"message": "Order deleted successfully"}

@app.delete("/orders")
async def delete_all_orders(
    current_user: User = Depends(get_current_admin_user)
):
    """Delete all orders (Admin only) - Use with caution!"""
    # Get count before deletion for reporting
    total_orders = await orders_collection.count_documents({})
    
    if total_orders == 0:
        return {"message": "No orders to delete", "deleted_count": 0}
    
    # Delete all orders
    result = await orders_collection.delete_many({})
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['ORDERS'],
        "bulk_delete",
        {
            "event_type": "orders_bulk_deleted",
            "deleted_count": result.deleted_count,
            "deleted_by": current_user.email
        }
    )
    
    return {
        "message": f"Successfully deleted {result.deleted_count} orders",
        "deleted_count": result.deleted_count
    }

# ==================== CART ROUTES ====================

@app.get("/cart", response_model=Cart)
async def get_cart(current_user: User = Depends(get_current_active_user)):
    cart = await carts_collection.find_one({"customer_id": current_user.id})
    if not cart:
        # Create empty cart
        cart_data = {
            "customer_id": current_user.id,
            "items": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await carts_collection.insert_one(cart_data)
        return Cart(**cart_data)
    
    cart["id"] = str(cart["_id"])
    return Cart(**cart)

@app.post("/cart/items")
async def add_to_cart(
    item: CartItem,
    current_user: User = Depends(get_current_active_user)
):
    # Verify product exists
    product = await products_collection.find_one({"_id": ObjectId(item.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get current cart
    cart = await carts_collection.find_one({"customer_id": current_user.id})
    
    if not cart:
        # Create new cart with the item
        cart_data = {
            "customer_id": current_user.id,
            "items": [item.dict()],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await carts_collection.insert_one(cart_data)
    else:
        # Check if product already exists in cart
        existing_item_index = None
        for i, cart_item in enumerate(cart.get("items", [])):
            if cart_item.get("product_id") == item.product_id:
                existing_item_index = i
                break
        
        if existing_item_index is not None:
            # Update quantity of existing item
            new_quantity = cart["items"][existing_item_index].get("quantity", 0) + item.quantity
            result = await carts_collection.update_one(
                {"customer_id": current_user.id},
                {
                    "$set": {
                        f"items.{existing_item_index}.quantity": new_quantity,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            # Add new item to cart
            result = await carts_collection.update_one(
                {"customer_id": current_user.id},
                {
                    "$push": {"items": item.dict()},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['CLICKSTREAM'],
        f"cart_{current_user.id}",
        {
            "event_type": "add_to_cart",
            "customer_id": current_user.id,
            "product_id": item.product_id,
            "quantity": item.quantity
        }
    )
    
    return {"message": "Item added to cart"}

@app.delete("/cart/items/{product_id}")
async def remove_from_cart(
    product_id: str,
    current_user: User = Depends(get_current_active_user)
):
    result = await carts_collection.update_one(
        {"customer_id": current_user.id},
        {
            "$pull": {"items": {"product_id": product_id}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Item removed from cart"}

@app.put("/cart/items/{product_id}")
async def update_cart_item_quantity(
    product_id: str,
    quantity: int = Query(..., description="New quantity for the item"),
    current_user: User = Depends(get_current_active_user)
):
    """Update quantity of a specific item in cart"""
    if quantity <= 0:
        # If quantity is 0 or negative, remove the item
        return await remove_from_cart(product_id, current_user)
    
    # Verify product exists
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update quantity
    result = await carts_collection.update_one(
        {
            "customer_id": current_user.id,
            "items.product_id": product_id
        },
        {
            "$set": {
                "items.$.quantity": quantity,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    return {"message": "Cart item quantity updated"}

@app.delete("/cart")
async def clear_cart(current_user: User = Depends(get_current_active_user)):
    """Clear entire cart"""
    result = await carts_collection.update_one(
        {"customer_id": current_user.id},
        {
            "$set": {
                "items": [],
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Cart cleared"}

@app.get("/cart/summary")
async def get_cart_summary(current_user: User = Depends(get_current_active_user)):
    """Get cart summary (total quantity and estimated total)"""
    cart = await carts_collection.find_one({"customer_id": current_user.id})
    
    if not cart or not cart.get("items"):
        return {
            "quantity": 0,
            "total": 0.0
        }
    
    total_quantity = sum(item.get("quantity", 0) for item in cart["items"])
    estimated_total = 0.0
    
    # Calculate total by fetching product prices
    for item in cart["items"]:
        product = await products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            estimated_total += product.get("price", 0) * item.get("quantity", 0)
    
    return {
        "quantity": total_quantity,
        "total": round(estimated_total, 2)
    }

@app.put("/cart/items")
async def bulk_update_cart_items(
    items: List[CartItem],
    current_user: User = Depends(get_current_active_user)
):
    """Bulk update cart items"""
    # Verify all products exist
    for item in items:
        product = await products_collection.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
    
    # Replace entire cart items
    result = await carts_collection.update_one(
        {"customer_id": current_user.id},
        {
            "$set": {
                "items": [item.dict() for item in items],
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return {"message": "Cart items updated"}

@app.post("/cart/checkout")
async def checkout_cart(
    checkout_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Convert cart to order"""
    # Get current cart
    cart = await carts_collection.find_one({"customer_id": current_user.id})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total and prepare order items
    total_amount = 0.0
    order_items = []
    
    for item in cart["items"]:
        product = await products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")
        
        item_total = product.get("price", 0) * item.get("quantity", 0)
        total_amount += item_total
        
        order_items.append({
            "product_id": item["product_id"],
            "quantity": item.get("quantity", 0),
            "price": product.get("price", 0),
            "product_name": product.get("name", "")
        })
    
    # Create order
    order_data = {
        "customer_id": current_user.id,
        "items": order_items,
        "total_amount": total_amount,
        "shipping_address": {"address": checkout_data.get("shipping_address", "")} if isinstance(checkout_data.get("shipping_address"), str) else checkout_data.get("shipping_address", {}),
        "billing_address": {"address": checkout_data.get("billing_address", "")} if isinstance(checkout_data.get("billing_address"), str) else checkout_data.get("billing_address", {}),
        "channel": "website"
    }
    
    result = await orders_collection.insert_one(order_data)
    
    # Clear cart after successful order
    await carts_collection.update_one(
        {"customer_id": current_user.id},
        {
            "$set": {
                "items": [],
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Send Kafka event
    send_kafka_event(
        kafka_producer,
        TOPICS['ORDERS'],
        f"order_{result.inserted_id}",
        {
            "event_type": "order_created_from_cart",
            "order_id": str(result.inserted_id),
            "customer_id": current_user.id,
            "total_amount": total_amount
        }
    )
    
    return {"order_id": str(result.inserted_id), "message": "Order created successfully"}

# ==================== EVENT TRACKING ====================

@app.post("/events")
async def track_event(event: Event):
    await events_collection.insert_one(event.dict())
    
    # Send Kafka event based on event type
    topic = TOPICS['USER_EVENTS']
    if event.event_type in ['add_to_cart', 'view_product', 'search']:
        topic = TOPICS['CLICKSTREAM']
    elif event.event_type in ['payment_success', 'payment_failed']:
        topic = TOPICS['PAYMENTS']
    
    send_kafka_event(
        kafka_producer,
        topic,
        f"event_{event.customer_id or 'anonymous'}",
        {
            "event_type": event.event_type,
            "customer_id": event.customer_id,
            "product_id": event.product_id,
            "session_id": event.session_id,
            "properties": event.properties,
            "timestamp": event.timestamp.isoformat()
        }
    )
    
    return {"status": "tracked"}

# ==================== ADMIN DASHBOARD ROUTES ====================

@app.get("/admin/stats")
async def get_admin_stats(current_user: User = Depends(get_current_admin_user)):
    # Get basic statistics
    total_users = await users_collection.count_documents({})
    total_products = await products_collection.count_documents({"is_active": True})
    total_orders = await orders_collection.count_documents({})
    total_revenue = 0
    
    # Calculate total revenue
    async for order in orders_collection.find({"status": {"$in": ["confirmed", "shipped", "delivered"]}}):
        total_revenue += order.get("total_amount", 0)
    
    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue
    }

@app.get("/admin/recent-orders")
async def get_recent_orders(
    limit: int = 10,
    current_user: User = Depends(get_current_admin_user)
):
    orders = []
    cursor = orders_collection.find().sort("created_at", -1).limit(limit)
    async for order in cursor:
        # Convert ObjectId to string and ensure all fields are properly formatted
        order["id"] = str(order["_id"])
        order.setdefault("status", "pending")
        order.setdefault("payment_status", "pending")
        order.setdefault("created_at", datetime.utcnow())
        order.setdefault("updated_at", datetime.utcnow())
        order.setdefault("channel", "website")
        
        # Fix: Coerce shipping_address and billing_address to dict if not already
        sa = order.get("shipping_address", {})
        if isinstance(sa, dict):
            order["shipping_address"] = sa
        elif isinstance(sa, str):
            order["shipping_address"] = {"address": sa}
        else:
            order["shipping_address"] = {}
        
        ba = order.get("billing_address", {})
        if isinstance(ba, dict):
            order["billing_address"] = ba
        elif isinstance(ba, str):
            order["billing_address"] = {"address": ba}
        else:
            order["billing_address"] = {}
        
        # Remove the original _id field to avoid serialization issues
        order.pop("_id", None)
        orders.append(order)
    return orders

# ==================== REAL-TIME ANALYTICS ROUTES ====================

@app.get("/analytics/fraud-summary")
async def get_fraud_summary(current_user: User = Depends(get_current_admin_user)):
    """Get fraud detection summary"""
    return realtime_analytics.get_fraud_summary()

@app.get("/analytics/stock-alerts")
async def get_stock_alerts_summary(current_user: User = Depends(get_current_admin_user)):
    """Get stock alerts summary"""
    return realtime_analytics.get_stock_alerts_summary()

@app.get("/analytics/order-tracking/{order_id}")
async def get_order_tracking(
    order_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get real-time order tracking information"""
    tracking_info = realtime_analytics.get_order_tracking_info(order_id)
    if not tracking_info:
        raise HTTPException(status_code=404, detail="Order tracking not found")
    
    # Check authorization
    if current_user.role == "customer" and tracking_info["customer_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return tracking_info

@app.post("/analytics/fraud-check")
async def check_transaction_fraud(
    transaction_data: dict,
    current_user: User = Depends(get_current_admin_user)
):
    """Check transaction for potential fraud"""
    fraud_result = realtime_analytics.analyze_transaction_fraud(transaction_data)
    
    # Send fraud detection event to Kafka
    send_fraud_event(kafka_producer, {
        **transaction_data,
        "fraud_analysis": fraud_result,
        "analyzed_by": current_user.email
    })
    
    # Send notification if fraud detected
    if fraud_result["is_fraudulent"]:
        notification_service.notify_fraud_alert(
            transaction_data.get("transaction_id", "unknown"),
            transaction_data.get("customer_id", "unknown"),
            transaction_data.get("amount", 0),
            ", ".join(fraud_result["risk_factors"]),
            fraud_result["risk_score"]
        )
    
    return fraud_result

@app.post("/analytics/stock-monitor")
async def monitor_stock_level(
    product_id: str,
    product_name: str,
    current_stock: int,
    threshold: Optional[int] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Monitor stock levels and generate alerts"""
    alert_info = realtime_analytics.monitor_stock_levels(
        product_id, product_name, current_stock, threshold
    )
    
    # Send stock alert to Kafka
    send_stock_alert(kafka_producer, alert_info)
    
    # Send notification if alert needed
    if alert_info["alert_needed"]:
        notification_service.notify_stock_alert(
            product_id, product_name, current_stock, threshold or 10
        )
    
    return alert_info

@app.post("/feedback")
async def submit_feedback(
    feedback_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Submit customer feedback for sentiment analysis"""
    try:
        # Store feedback in MongoDB
        feedback_doc = {
            "text": feedback_data.get("text", ""),
            "feedback_type": feedback_data.get("feedback_type", "review"),
            "rating": feedback_data.get("rating"),
            "category": feedback_data.get("category"),
            "product_id": feedback_data.get("product_id"),
            "order_id": feedback_data.get("order_id"),
            "user_id": str(current_user.id),
            "source": feedback_data.get("source", "website"),
            "metadata": feedback_data.get("metadata", {}),
            "created_at": datetime.utcnow(),
            "processed": False
        }
        
        result = await feedback_collection.insert_one(feedback_doc)
        
        # Store in MongoDB - Databricks can read directly from MongoDB
        
        return {
            "feedback_id": str(result.inserted_id),
            "status": "submitted",
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

@app.post("/feedback/test")
async def submit_feedback_test(feedback_data: dict):
    """Submit customer feedback for sentiment analysis (no auth required)"""
    try:
        # Store feedback in MongoDB
        feedback_doc = {
            "text": feedback_data.get("text", ""),
            "feedback_type": feedback_data.get("feedback_type", "review"),
            "rating": feedback_data.get("rating"),
            "category": feedback_data.get("category"),
            "product_id": feedback_data.get("product_id"),
            "order_id": feedback_data.get("order_id"),
            "user_id": "test_user",
            "source": feedback_data.get("source", "website"),
            "metadata": feedback_data.get("metadata", {}),
            "created_at": datetime.utcnow(),
            "processed": False
        }
        
        result = await feedback_collection.insert_one(feedback_doc)
        
        # Store in MongoDB - Databricks can read directly from MongoDB
        
        return {
            "feedback_id": str(result.inserted_id),
            "status": "submitted",
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

@app.get("/feedback/summary")
async def get_feedback_summary(
    current_user: User = Depends(get_current_active_user)
):
    """Get feedback summary statistics"""
    try:
        # Only allow users to see their own feedback unless admin
        query = {}
        if current_user.role not in ["admin", "super_admin"]:
            query["user_id"] = str(current_user.id)
        
        total_feedback = await feedback_collection.count_documents(query)
        processed_feedback = await feedback_collection.count_documents({**query, "processed": True})
        
        return {
            "total_feedback": total_feedback,
            "processed_feedback": processed_feedback,
            "pending_analysis": total_feedback - processed_feedback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback summary: {str(e)}")

@app.get("/feedback/product/{product_id}")
async def get_product_feedback(product_id: str):
    """Get feedback for a specific product"""
    try:
        # Get feedback for the product
        feedback_cursor = feedback_collection.find(
            {"product_id": product_id},
            {"_id": 1, "text": 1, "rating": 1, "feedback_type": 1, "created_at": 1, "user_id": 1, "sentiment_score": 1, "sentiment_label": 1}
        ).sort("created_at", -1)
        
        feedback_list = []
        async for feedback in feedback_cursor:
            # Get user name if available
            user_name = None
            if feedback.get("user_id"):
                user = await users_collection.find_one({"_id": feedback["user_id"]})
                if user:
                    user_name = user.get("name", "Anonymous")
            
            feedback_list.append({
                "id": str(feedback["_id"]),
                "text": feedback["text"],
                "rating": feedback["rating"],
                "feedback_type": feedback["feedback_type"],
                "created_at": feedback["created_at"].isoformat() if feedback.get("created_at") else None,
                "user_name": user_name,
                "sentiment_score": feedback.get("sentiment_score"),
                "sentiment_label": feedback.get("sentiment_label")
            })
        
        return {
            "product_id": product_id,
            "feedback": feedback_list,
            "total_reviews": len(feedback_list),
            "average_rating": sum(f["rating"] for f in feedback_list) / len(feedback_list) if feedback_list else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get product feedback: {str(e)}")

@app.get("/feedback/all")
async def get_all_feedback(
    current_user: User = Depends(get_current_admin_user)
):
    """Get all feedback for admin dashboard"""
    try:
        # Get all feedback with product information
        feedback_cursor = feedback_collection.find().sort("created_at", -1)
        
        feedback_list = []
        async for feedback in feedback_cursor:
            # Get user name if available
            user_name = None
            if feedback.get("user_id"):
                user = await users_collection.find_one({"_id": feedback["user_id"]})
                if user:
                    user_name = user.get("name", "Anonymous")
            
            # Get product name if available
            product_name = None
            if feedback.get("product_id"):
                product = await products_collection.find_one({"_id": feedback["product_id"]})
                if product:
                    product_name = product.get("name", "Unknown Product")
            
            feedback_list.append({
                "id": str(feedback["_id"]),
                "text": feedback["text"],
                "rating": feedback["rating"],
                "feedback_type": feedback["feedback_type"],
                "created_at": feedback["created_at"].isoformat() if feedback.get("created_at") else None,
                "user_name": user_name,
                "product_id": feedback.get("product_id"),
                "product_name": product_name,
                "sentiment_score": feedback.get("sentiment_score"),
                "sentiment_label": feedback.get("sentiment_label")
            })
        
        return {
            "feedback": feedback_list,
            "total_count": len(feedback_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get all feedback: {str(e)}")

@app.post("/notifications/test")
async def test_notification(
    notification_type: str,
    test_data: dict,
    current_user: User = Depends(get_current_admin_user)
):
    """Test notification system"""
    if notification_type == "order_status":
        notification_service.notify_order_status_change(
            test_data.get("order_id", "test_123"),
            test_data.get("customer_email", "test@example.com"),
            test_data.get("old_status", "pending"),
            test_data.get("new_status", "confirmed"),
            test_data.get("order_details", {})
        )
    elif notification_type == "stock_alert":
        notification_service.notify_stock_alert(
            test_data.get("product_id", "test_123"),
            test_data.get("product_name", "Test Product"),
            test_data.get("current_stock", 5),
            test_data.get("threshold", 10)
        )
    elif notification_type == "fraud_alert":
        notification_service.notify_fraud_alert(
            test_data.get("transaction_id", "test_123"),
            test_data.get("customer_id", "test_123"),
            test_data.get("amount", 100.0),
            test_data.get("reason", "Test fraud alert"),
            test_data.get("risk_score", 0.8)
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid notification type")
    
    return {"message": f"Test {notification_type} notification sent"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
