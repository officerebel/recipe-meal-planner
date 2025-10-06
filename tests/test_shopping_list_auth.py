#!/usr/bin/env python3
"""
Test shopping list generation with authentication
"""
import requests
import json

API_BASE = "https://proud-mercy-production.up.railway.app/api"

def test_with_auth():
    """Test shopping list generation with authentication"""
    print("🧪 Testing Shopping List with Authentication...")
    
    # First, create a test user and get token
    print("👤 Creating test user...")
    
    import random
    random_id = random.randint(1000, 9999)
    register_data = {
        "username": f"testuser{random_id}",
        "email": f"test{random_id}@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        # Register user
        response = requests.post(
            f"{API_BASE}/auth/register/",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration status: {response.status_code}")
        print(f"Registration response: {response.text}")
        
        if response.status_code == 201:
            print("✅ User registered successfully")
            data = response.json()
            token = data.get('token')
        elif response.status_code == 400:
            # User might already exist, try login
            print("ℹ️ User might exist, trying login...")
            login_response = requests.post(
                f"{API_BASE}/auth/login/",
                json={
                    "email": register_data["email"],
                    "password": register_data["password"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                print("✅ User logged in successfully")
                data = login_response.json()
                token = data.get('token')
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return False
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        if not token:
            print("❌ No token received")
            return False
        
        print(f"🔑 Got token: {token[:20]}...")
        
        # Now test shopping list generation
        print("\n📝 Testing shopping list generation...")
        
        shopping_list_data = {
            "name": "Test Shopping List",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "meal_plan_ids": []
        }
        
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/shopping-lists/generate/",
            json=shopping_list_data,
            headers=headers
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Shopping list created successfully!")
            data = response.json()
            print(f"📄 Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Shopping list creation failed")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_with_auth()
    if success:
        print("\n🎉 Shopping list generation is working on Railway!")
    else:
        print("\n❌ Shopping list generation still has issues")