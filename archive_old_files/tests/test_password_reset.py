#!/usr/bin/env python3
"""
Test password reset functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_password_reset():
    """Test password reset functionality"""
    print("=== Testing Password Reset ===")
    
    # Login first
    login_data = {
        "email": "demo@example.com", 
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"Got token: {token[:20]}...")
            
            # Test password reset endpoint
            headers = {"Authorization": f"Token {token}"}
            
            # Test password reset
            reset_data = {
                "new_password": "newpassword123"
            }
            
            response = requests.post(f"{BASE_URL}/auth/reset-password/", 
                                   json=reset_data, headers=headers)
            print(f"Password reset: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Password reset successful")
                new_data = response.json()
                new_token = new_data.get('token')
                print(f"Got new token: {new_token[:20] if new_token else 'None'}...")
                
                # Test login with new password
                login_data_new = {
                    "email": "demo@example.com", 
                    "password": "newpassword123"
                }
                
                response = requests.post(f"{BASE_URL}/auth/login/", json=login_data_new)
                print(f"Login with new password: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Login with new password successful")
                    
                    # Reset password back to original
                    token = response.json().get('token')
                    headers = {"Authorization": f"Token {token}"}
                    
                    reset_back_data = {
                        "new_password": "demo123"
                    }
                    
                    response = requests.post(f"{BASE_URL}/auth/reset-password/", 
                                           json=reset_back_data, headers=headers)
                    print(f"Reset password back: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✅ Password restored to original")
                else:
                    print("❌ Login with new password failed")
            else:
                print(f"❌ Password reset failed: {response.json()}")
        else:
            print(f"❌ Login failed: {response.json()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🔍 Testing Password Reset Functionality")
    print("=" * 50)
    test_password_reset()