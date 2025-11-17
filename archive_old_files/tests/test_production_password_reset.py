#!/usr/bin/env python3
"""
Test password reset on production
"""
import requests
import json

BASE_URL = "https://proud-mercy-production.up.railway.app/api"

def test_production_password_reset():
    """Test password reset on production"""
    print("=== Testing Production Password Reset ===")
    
    # First, try to login with admin user
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        # Try to login with admin user
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
        else:
            print(f"Login failed: {response.text}")
            return
        
        if not token:
            print("No token received")
            return
            
        print(f"Got token: {token[:20]}...")
        
        # Test password reset endpoint
        headers = {"Authorization": f"Token {token}"}
        
        # Check if endpoint exists
        response = requests.options(f"{BASE_URL}/auth/reset-password/", headers=headers)
        print(f"Reset password endpoint OPTIONS: {response.status_code}")
        
        # Test password reset
        reset_data = {
            "new_password": "newtestpass123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/reset-password/", 
                               json=reset_data, headers=headers)
        print(f"Password reset: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Password reset successful")
            result = response.json()
            print(f"Response: {result}")
        else:
            print(f"❌ Password reset failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_production_password_reset()