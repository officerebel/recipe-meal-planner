#!/usr/bin/env python3
"""
Simple authentication test
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_endpoints():
    """Test basic endpoint availability"""
    print("=== Testing Endpoint Availability ===")
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health/")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test auth endpoints
    auth_endpoints = [
        "/auth/login/",
        "/auth/logout/", 
        "/auth/register/",
        "/auth/user/"
    ]
    
    for endpoint in auth_endpoints:
        try:
            response = requests.options(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {response.status_code} (OPTIONS)")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")

def test_login_logout():
    """Test login and logout flow"""
    print("\n=== Testing Login/Logout Flow ===")
    
    # First, try to register a test user
    register_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
        print(f"Register attempt: {response.status_code}")
        if response.status_code not in [200, 201, 400]:  # 400 might be "user exists"
            print(f"Register response: {response.text[:200]}")
    except Exception as e:
        print(f"Register error: {e}")
    
    # Try to login
    login_data = {
        "email": "demo@example.com", 
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Login attempt: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"Login successful, got token: {token[:20] if token else 'None'}...")
            
            if token:
                # Test logout
                headers = {"Authorization": f"Token {token}"}
                logout_response = requests.post(f"{BASE_URL}/auth/logout/", headers=headers)
                print(f"Logout attempt: {logout_response.status_code}")
                
                if logout_response.status_code == 200:
                    print("✅ Logout successful")
                else:
                    print(f"❌ Logout failed: {logout_response.text[:200]}")
        else:
            print(f"❌ Login failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"Login error: {e}")

def test_password_change():
    """Test if password change endpoint exists"""
    print("\n=== Testing Password Change Availability ===")
    
    # Check if there's a password change endpoint
    password_endpoints = [
        "/auth/change-password/",
        "/auth/password/change/", 
        "/auth/password-change/",
        "/password/change/",
        "/change-password/"
    ]
    
    for endpoint in password_endpoints:
        try:
            response = requests.options(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ Found password change endpoint!")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")

if __name__ == "__main__":
    print("🔍 Simple Authentication Test")
    print("=" * 50)
    
    test_endpoints()
    test_login_logout()
    test_password_change()