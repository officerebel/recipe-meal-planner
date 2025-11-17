#!/usr/bin/env python3
"""
Test password change functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_password_change():
    """Test password change flow"""
    print("=== Testing Password Change ===")
    
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
            
            # Test password change endpoint availability
            headers = {"Authorization": f"Token {token}"}
            response = requests.options(f"{BASE_URL}/auth/change-password/", headers=headers)
            print(f"Password change endpoint: {response.status_code}")
            
            # Test password change with wrong current password
            change_data = {
                "current_password": "wrongpassword",
                "new_password": "newpassword123"
            }
            
            response = requests.post(f"{BASE_URL}/auth/change-password/", 
                                   json=change_data, headers=headers)
            print(f"Wrong current password test: {response.status_code}")
            if response.status_code != 200:
                print(f"  Response: {response.json()}")
            
            # Test password change with correct current password
            change_data = {
                "current_password": "demo123",
                "new_password": "newdemo123"
            }
            
            response = requests.post(f"{BASE_URL}/auth/change-password/", 
                                   json=change_data, headers=headers)
            print(f"Correct password change: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Password change successful")
                new_data = response.json()
                new_token = new_data.get('token')
                print(f"Got new token: {new_token[:20] if new_token else 'None'}...")
                
                # Test login with new password
                login_data_new = {
                    "email": "demo@example.com", 
                    "password": "newdemo123"
                }
                
                response = requests.post(f"{BASE_URL}/auth/login/", json=login_data_new)
                print(f"Login with new password: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Login with new password successful")
                    
                    # Change password back to original
                    token = response.json().get('token')
                    headers = {"Authorization": f"Token {token}"}
                    
                    change_back_data = {
                        "current_password": "newdemo123",
                        "new_password": "demo123"
                    }
                    
                    response = requests.post(f"{BASE_URL}/auth/change-password/", 
                                           json=change_back_data, headers=headers)
                    print(f"Change password back: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✅ Password restored to original")
                else:
                    print("❌ Login with new password failed")
            else:
                print(f"❌ Password change failed: {response.json()}")
        else:
            print(f"❌ Login failed: {response.json()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🔍 Testing Password Change Functionality")
    print("=" * 50)
    test_password_change()