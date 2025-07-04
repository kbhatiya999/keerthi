#!/usr/bin/env python3
import requests
import json

def test_backend_endpoints():
    base_url = "http://localhost:8000"
    
    print("=== Testing Backend Endpoints ===\n")
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test login endpoint
    print("2. Testing login endpoint...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                print(f"   Token received: {token[:50]}...")
                print()
                
                # Test feedback endpoint with token
                print("3. Testing feedback endpoint with authentication...")
                feedback_data = {
                    "product_id": "6861af71da45d047a056e298",
                    "rating": 5,
                    "comment": "This is a test feedback from backend testing script",
                    "sentiment": "positive"
                }
                
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post(f"{base_url}/feedback", json=feedback_data, headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                print()
                
                # Test getting feedback for a product
                print("4. Testing get feedback for product...")
                response = requests.get(f"{base_url}/feedback/product/6861af71da45d047a056e298")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                print()
                
                # Test admin feedback overview
                print("5. Testing admin feedback overview...")
                response = requests.get(f"{base_url}/feedback/admin/overview", headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                print()
                
            else:
                print("   No token found in response")
        else:
            print("   Login failed")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("=== End of Testing ===")

if __name__ == "__main__":
    test_backend_endpoints() 