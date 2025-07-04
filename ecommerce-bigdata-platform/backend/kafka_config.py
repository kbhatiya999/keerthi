import os
from confluent_kafka import Producer, Consumer
from dotenv import load_dotenv
import time

load_dotenv()

# Confluent Cloud Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'security.protocol': os.getenv('KAFKA_SECURITY_PROTOCOL', 'SASL_SSL'),
    'sasl.mechanisms': os.getenv('KAFKA_SASL_MECHANISM', 'PLAIN'),
    'sasl.username': os.getenv('KAFKA_API_KEY'),
    'sasl.password': os.getenv('KAFKA_API_SECRET'),
    'client.id': 'ecommerce-backend'
}

# Kafka Topics - Extended for real-time analytics
TOPICS = {
    'CLICKSTREAM': os.getenv('KAFKA_TOPIC_CLICKSTREAM', 'ecommerce-clickstream'),
    'ORDERS': os.getenv('KAFKA_TOPIC_ORDERS', 'ecommerce-orders'),
    'PAYMENTS': os.getenv('KAFKA_TOPIC_PAYMENTS', 'ecommerce-payments'),
    'INVENTORY': os.getenv('KAFKA_TOPIC_INVENTORY', 'ecommerce-inventory'),
    'USER_EVENTS': os.getenv('KAFKA_TOPIC_USER_EVENTS', 'ecommerce-user-events'),
    # New topics for Phase 1 real-time features
    'FRAUD_DETECTION': os.getenv('KAFKA_TOPIC_FRAUD', 'ecommerce-fraud-detection'),
    'STOCK_ALERTS': os.getenv('KAFKA_TOPIC_STOCK_ALERTS', 'ecommerce-stock-alerts'),
    'ORDER_TRACKING': os.getenv('KAFKA_TOPIC_ORDER_TRACKING', 'ecommerce-order-tracking'),
    'NOTIFICATIONS': os.getenv('KAFKA_TOPIC_NOTIFICATIONS', 'ecommerce-notifications')
}

def get_kafka_producer():
    """Get a Kafka producer instance"""
    return Producer(KAFKA_CONFIG)

def get_kafka_consumer(group_id: str, topics: list):
    """Get a Kafka consumer instance"""
    consumer_config = KAFKA_CONFIG.copy()
    consumer_config.update({
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 1000
    })
    consumer = Consumer(consumer_config)
    consumer.subscribe(topics)
    return consumer

def delivery_report(err, msg):
    """Delivery report callback for Kafka producer"""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

def send_kafka_event(producer: Producer, topic: str, key: str, value: dict):
    """Send an event to Kafka"""
    # Check if Kafka is properly configured
    if not producer or not os.getenv('KAFKA_BOOTSTRAP_SERVERS'):
        print(f"Kafka not configured, skipping event: {value}")
        return
        
    try:
        producer.produce(
            topic=topic,
            key=key.encode('utf-8'),
            value=str(value).encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)  # Trigger delivery reports
        print(f"Event sent to topic {topic}: {value}")
    except Exception as e:
        print(f"Warning: Error sending event to Kafka: {e}")
        # Don't raise the exception - just log it as a warning
        # This prevents Kafka issues from crashing the API endpoints

def send_fraud_event(producer: Producer, transaction_data: dict):
    """Send fraud detection event to Kafka"""
    key = f"fraud_{transaction_data.get('customer_id', 'unknown')}_{int(time.time())}"
    send_kafka_event(producer, TOPICS['FRAUD_DETECTION'], key, transaction_data)

def send_stock_alert(producer: Producer, alert_data: dict):
    """Send stock alert event to Kafka"""
    key = f"stock_{alert_data.get('product_id', 'unknown')}"
    send_kafka_event(producer, TOPICS['STOCK_ALERTS'], key, alert_data)

def send_order_tracking_event(producer: Producer, tracking_data: dict):
    """Send order tracking event to Kafka"""
    key = f"order_{tracking_data.get('order_id', 'unknown')}"
    send_kafka_event(producer, TOPICS['ORDER_TRACKING'], key, tracking_data)

def send_notification_event(producer: Producer, notification_data: dict):
    """Send notification event to Kafka"""
    key = f"notification_{notification_data.get('type', 'unknown')}_{int(time.time())}"
    send_kafka_event(producer, TOPICS['NOTIFICATIONS'], key, notification_data) 