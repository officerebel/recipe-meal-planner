#!/usr/bin/env python3
"""
Test script to debug shopping list generation 500 error
"""
import requests
import json

# Test the shopping list generation endpoint
API_BASE = "https://proud-mercy-production.up.railway.app/api"

def test_shopping_list_generation():
    """Test shopping list generation with sample data"""
    
    # First, let's check if we can access the endpoint
    print("🧪 Testing Shopping List Generation...")
    
    # Test data for shopping list generation
    test_data = {
        "name": "Test Shopping List",
        "meal_plan_ids": [],  # Empty for now to test basic functionality
        "family": 1  # Assuming family ID 1 exists
    }
    
    try:
        # Test the generate endpoint
        print(f"📡 POST {API_BASE}/shopping-lists/generate/")
        print(f"📦 Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{API_BASE}/shopping-lists/generate/",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error")
            print(f"📄 Response Text: {response.text}")
            
            # Try to get more details
            try:
                error_data = response.json()
                print(f"📄 Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print("📄 Response is not valid JSON")
        
        elif response.status_code == 200 or response.status_code == 201:
            print("✅ Success!")
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)}")
        
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Also test the regular create endpoint
    print("\n" + "="*50)
    print("🧪 Testing Regular Shopping List Creation...")
    
    try:
        response = requests.post(
            f"{API_BASE}/shopping-lists/",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error")
            print(f"📄 Response Text: {response.text}")
        elif response.status_code in [200, 201]:
            print("✅ Success!")
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"⚠️ Status code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_shopping_list_generation()