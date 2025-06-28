from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="E-commerce BigData API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "E-commerce BigData Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from models import Product, Customer, Order, Event
from database import products_collection, customers_collection, orders_collection, events_collection

@app.post("/products/")
async def create_product(product: Product):
    result = await products_collection.insert_one(product.dict())
    return {"id": str(result.inserted_id)}

@app.get("/products/")
async def get_products():
    products = []
    async for product in products_collection.find():
        product["_id"] = str(product["_id"])
        products.append(product)
    return products

@app.post("/orders/")
async def create_order(order: Order):
    # Create order
    result = await orders_collection.insert_one(order.dict())
    
    # Emit event for analytics
    event = Event(
        event_type="order_created",
        customer_id=order.customer_id,
        properties={
            "order_id": str(result.inserted_id),
            "total_amount": order.total_amount,
            "channel": order.channel
        }
    )
    await events_collection.insert_one(event.dict())
    
    return {"order_id": str(result.inserted_id)}

@app.post("/events/")
async def track_event(event: Event):
    await events_collection.insert_one(event.dict())
    return {"status": "tracked"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
