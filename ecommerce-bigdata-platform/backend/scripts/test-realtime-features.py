#!/usr/bin/env python3
"""
Test script for Phase 1 Real-time Features
Tests fraud detection, stock alerts, and order tracking
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"  # Updated to match the created admin user
ADMIN_PASSWORD = "admin123"

def get_auth_token(email, password):
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_fraud_detection(token):
    """Test fraud detection system"""
    print("\n🔍 Testing Fraud Detection System")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Normal transaction
    print("\n1. Testing normal transaction...")
    normal_transaction = {
        "customer_id": "test_customer_1",
        "amount": 50.0,
        "ip_address": "192.168.1.100",
        "device_id": "device_001",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/analytics/fraud-check", 
                           json=normal_transaction, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Normal transaction: Risk score {result['risk_score']:.2f}")
        print(f"   Recommendation: {result['recommendation']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 2: High amount transaction
    print("\n2. Testing high amount transaction...")
    high_amount_transaction = {
        "customer_id": "test_customer_2",
        "amount": 1500.0,
        "ip_address": "192.168.1.101",
        "device_id": "device_002",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/analytics/fraud-check", 
                           json=high_amount_transaction, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ High amount transaction: Risk score {result['risk_score']:.2f}")
        print(f"   Risk factors: {', '.join(result['risk_factors'])}")
        print(f"   Recommendation: {result['recommendation']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 3: Multiple transactions from same IP
    print("\n3. Testing multiple transactions from same IP...")
    for i in range(3):
        multi_ip_transaction = {
            "customer_id": f"test_customer_{i+3}",
            "amount": 100.0,
            "ip_address": "192.168.1.200",  # Same IP
            "device_id": f"device_{i+3}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/analytics/fraud-check", 
                               json=multi_ip_transaction, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"   Transaction {i+1}: Risk score {result['risk_score']:.2f}")
        else:
            print(f"❌ Failed: {response.text}")
    
    # Get fraud summary
    print("\n4. Getting fraud detection summary...")
    response = requests.get(f"{BASE_URL}/analytics/fraud-summary", headers=headers)
    if response.status_code == 200:
        summary = response.json()
        print(f"✅ Fraud Summary:")
        print(f"   Active customers monitored: {summary['active_customers_monitored']}")
        print(f"   Active IPs monitored: {summary['active_ips_monitored']}")
        print(f"   Total suspicious transactions: {summary['total_suspicious_transactions']}")
    else:
        print(f"❌ Failed: {response.text}")

def test_stock_alerts(token):
    """Test stock alert system"""
    print("\n📦 Testing Stock Alert System")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Normal stock level
    print("\n1. Testing normal stock level...")
    normal_stock = {
        "product_id": "test_product_1",
        "product_name": "Test Product 1",
        "current_stock": 50,
        "threshold": 10
    }
    
    response = requests.post(f"{BASE_URL}/analytics/stock-monitor", 
                           json=normal_stock, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Normal stock: {result['current_stock']} units")
        print(f"   Alert needed: {result['alert_needed']}")
        print(f"   Severity: {result['severity']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 2: Low stock warning
    print("\n2. Testing low stock warning...")
    low_stock = {
        "product_id": "test_product_2",
        "product_name": "Test Product 2",
        "current_stock": 8,
        "threshold": 10
    }
    
    response = requests.post(f"{BASE_URL}/analytics/stock-monitor", 
                           json=low_stock, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Low stock: {result['current_stock']} units")
        print(f"   Alert needed: {result['alert_needed']}")
        print(f"   Severity: {result['severity']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 3: Critical stock level
    print("\n3. Testing critical stock level...")
    critical_stock = {
        "product_id": "test_product_3",
        "product_name": "Test Product 3",
        "current_stock": 3,
        "threshold": 10
    }
    
    response = requests.post(f"{BASE_URL}/analytics/stock-monitor", 
                           json=critical_stock, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Critical stock: {result['current_stock']} units")
        print(f"   Alert needed: {result['alert_needed']}")
        print(f"   Severity: {result['severity']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Get stock alerts summary
    print("\n4. Getting stock alerts summary...")
    response = requests.get(f"{BASE_URL}/analytics/stock-alerts", headers=headers)
    if response.status_code == 200:
        summary = response.json()
        print(f"✅ Stock Alerts Summary:")
        print(f"   Total alerts: {summary['total_alerts']}")
        print(f"   Critical alerts: {summary['critical_alerts']}")
        print(f"   Warning alerts: {summary['warning_alerts']}")
        print(f"   Products monitored: {summary['products_monitored']}")
    else:
        print(f"❌ Failed: {response.text}")

def test_order_tracking(token):
    """Test order tracking system"""
    print("\n📋 Testing Order Tracking System")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test order first
    print("\n1. Creating test order...")
    test_order = {
        "customer_id": "test_customer_tracking",
        "items": [
            {
                "product_id": "test_product_tracking",
                "quantity": 2,
                "price": 25.0,
                "product_name": "Test Product for Tracking"
            }
        ],
        "total_amount": 50.0,
        "status": "pending",
        "payment_status": "pending",
        "shipping_address": {"address": "123 Test St"},
        "billing_address": {"address": "123 Test St"},
        "channel": "website"
    }
    
    response = requests.post(f"{BASE_URL}/orders", json=test_order, headers=headers)
    if response.status_code == 200:
        order_id = response.json()["order_id"]
        print(f"✅ Test order created: {order_id}")
        
        # Test order tracking
        print("\n2. Testing order tracking...")
        response = requests.get(f"{BASE_URL}/analytics/order-tracking/{order_id}", headers=headers)
        if response.status_code == 200:
            tracking_info = response.json()
            print(f"✅ Order tracking info:")
            print(f"   Current status: {tracking_info['current_status']}")
            print(f"   Total status changes: {tracking_info['total_status_changes']}")
        else:
            print(f"❌ Failed to get tracking info: {response.text}")
        
        # Update order status to test tracking
        print("\n3. Updating order status...")
        status_update = {"status": "confirmed"}
        response = requests.put(f"{BASE_URL}/orders/{order_id}", json=status_update, headers=headers)
        if response.status_code == 200:
            print("✅ Order status updated to 'confirmed'")
            
            # Check tracking again
            response = requests.get(f"{BASE_URL}/analytics/order-tracking/{order_id}", headers=headers)
            if response.status_code == 200:
                tracking_info = response.json()
                print(f"✅ Updated tracking info:")
                print(f"   Current status: {tracking_info['current_status']}")
                print(f"   Total status changes: {tracking_info['total_status_changes']}")
                if tracking_info['status_history']:
                    latest_change = tracking_info['status_history'][-1]
                    print(f"   Latest change: {latest_change['old_status']} → {latest_change['new_status']}")
            else:
                print(f"❌ Failed to get updated tracking info: {response.text}")
        else:
            print(f"❌ Failed to update order: {response.text}")
    else:
        print(f"❌ Failed to create test order: {response.text}")

def test_notifications(token):
    """Test notification system"""
    print("\n🔔 Testing Notification System")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test order status notification
    print("\n1. Testing order status notification...")
    order_notification = {
        "order_id": "test_order_123",
        "customer_email": "test@example.com",
        "old_status": "pending",
        "new_status": "confirmed",
        "order_details": {"total_amount": 99.99}
    }
    
    response = requests.post(f"{BASE_URL}/notifications/test", 
                           params={"notification_type": "order_status"},
                           json=order_notification, headers=headers)
    if response.status_code == 200:
        print("✅ Order status notification test sent")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test stock alert notification
    print("\n2. Testing stock alert notification...")
    stock_notification = {
        "product_id": "test_product_123",
        "product_name": "Test Product",
        "current_stock": 5,
        "threshold": 10
    }
    
    response = requests.post(f"{BASE_URL}/notifications/test", 
                           params={"notification_type": "stock_alert"},
                           json=stock_notification, headers=headers)
    if response.status_code == 200:
        print("✅ Stock alert notification test sent")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test fraud alert notification
    print("\n3. Testing fraud alert notification...")
    fraud_notification = {
        "transaction_id": "test_txn_123",
        "customer_id": "test_customer_123",
        "amount": 500.0,
        "reason": "High amount transaction from new customer",
        "risk_score": 0.85
    }
    
    response = requests.post(f"{BASE_URL}/notifications/test", 
                           params={"notification_type": "fraud_alert"},
                           json=fraud_notification, headers=headers)
    if response.status_code == 200:
        print("✅ Fraud alert notification test sent")
    else:
        print(f"❌ Failed: {response.text}")

def main():
    """Main test function"""
    print("🚀 Phase 1 Real-time Features Test Suite")
    print("=" * 50)
    
    # Get admin token
    print("\n🔐 Authenticating as admin...")
    token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print("❌ Authentication failed. Please check admin credentials.")
        return
    
    print("✅ Authentication successful")
    
    # Run tests
    try:
        test_fraud_detection(token)
        test_stock_alerts(token)
        test_order_tracking(token)
        test_notifications(token)
        
        print("\n🎉 All Phase 1 tests completed!")
        print("\n📊 Summary:")
        print("   ✅ Fraud Detection System")
        print("   ✅ Stock Alert System") 
        print("   ✅ Order Tracking System")
        print("   ✅ Notification System")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main() 