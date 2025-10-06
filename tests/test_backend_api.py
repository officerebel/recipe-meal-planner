#!/usr/bin/env python3
"""
Test script to check if the backend API is responding
"""
import requests
import json

def test_backend_api():
    """Test if the backend API is responding"""
    base_url = "https://proud-mercy-production.up.railway.app"
    
    print("🔍 Testing backend API connectivity...")
    
    # Test endpoints
    endpoints = [
        "/",  # Root endpoint
        "/api/",  # API root
        "/api/auth/",  # Auth endpoints
        "/api/recipes/",  # Recipes endpoint
        "/api/meal-plans/",  # Meal plans endpoint
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"\n📡 Testing: {url}")
            response = requests.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS")
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print(f"   Response: {response.text[:200]}...")
                else:
                    print(f"   Response: {response.text[:200]}...")
            elif response.status_code == 401:
                print(f"   ⚠️  UNAUTHORIZED (expected for protected endpoints)")
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND")
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT (>10s)")
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ CONNECTION ERROR: {e}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    # Test specific API functionality
    print(f"\n🧪 Testing API functionality...")
    
    # Test registration endpoint
    try:
        url = f"{base_url}/api/auth/register/"
        print(f"\n📡 Testing registration endpoint: {url}")
        
        # Send invalid data to test if endpoint exists
        response = requests.post(url, json={}, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 400:
            print(f"   ✅ ENDPOINT EXISTS (400 = validation error expected)")
        elif response.status_code == 405:
            print(f"   ❌ METHOD NOT ALLOWED")
        else:
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    test_backend_api()