#!/usr/bin/env python3
"""
Simple script to setup production data via API calls
This can be run locally to setup the deployed backend
"""
import requests
import json

# Use the deployed backend URL
BACKEND_URL = "https://proud-mercy-production.up.railway.app"

def setup_production_data():
    """Setup production data via API calls"""
    print("🚀 Setting up production data...")
    
    # First, try to register a demo user
    register_data = {
        "email": "demo@example.com",
        "password": "demo123",
        "first_name": "Demo",
        "last_name": "User"
    }
    
    try:
        print("Creating demo user...")
        response = requests.post(f"{BACKEND_URL}/api/auth/register/", json=register_data)
        
        if response.status_code in [200, 201]:
            print("✅ Demo user created successfully")
            data = response.json()
            token = data.get('token')
        elif response.status_code == 400:
            # User might already exist, try to login
            print("User might exist, trying to login...")
            login_response = requests.post(f"{BACKEND_URL}/api/auth/login/", json={
                "email": "demo@example.com",
                "password": "demo123"
            })
            
            if login_response.status_code == 200:
                print("✅ Logged in successfully")
                data = login_response.json()
                token = data.get('token')
            else:
                print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
                return
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return
        
        if not token:
            print("❌ No token received")
            return
        
        print(f"Got authentication token: {token[:20]}...")
        
        # Now try to call the setup endpoint
        headers = {"Authorization": f"Token {token}"}
        
        print("Calling setup endpoint...")
        setup_response = requests.post(f"{BACKEND_URL}/api/setup/", headers=headers)
        
        if setup_response.status_code == 200:
            print("✅ Setup endpoint called successfully")
            print(setup_response.json())
        else:
            print(f"⚠️ Setup endpoint response: {setup_response.status_code} - {setup_response.text}")
        
        # Test if we can fetch recipes
        print("Testing recipes endpoint...")
        recipes_response = requests.get(f"{BACKEND_URL}/api/recipes/", headers=headers)
        
        if recipes_response.status_code == 200:
            recipes_data = recipes_response.json()
            recipe_count = recipes_data.get('count', 0)
            print(f"✅ Found {recipe_count} recipes in database")
        else:
            print(f"⚠️ Recipes endpoint: {recipes_response.status_code} - {recipes_response.text}")
        
        print("🎉 Production setup completed!")
        print(f"🔗 Frontend: https://mealplannerfrontend-production.up.railway.app")
        print(f"🔗 Backend: {BACKEND_URL}")
        print(f"🔐 Login: demo@example.com / demo123")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")

if __name__ == "__main__":
    setup_production_data()