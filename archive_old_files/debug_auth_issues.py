#!/usr/bin/env python3
"""
Debug authentication and family management issues
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_login():
    """Test login to get a token"""
    print("=== Testing Login ===")
    response = requests.post(f"{BASE_URL}/auth/login/", {
        "email": "demo@example.com",
        "password": "demo123"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✅ Login successful, token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_logout(token):
    """Test logout endpoint"""
    print("\n=== Testing Logout ===")
    headers = {"Authorization": f"Token {token}"}
    response = requests.post(f"{BASE_URL}/auth/logout/", headers=headers)
    
    if response.status_code == 200:
        print("✅ Logout successful")
        return True
    else:
        print(f"❌ Logout failed: {response.status_code} - {response.text}")
        return False

def test_family_endpoints(token):
    """Test family management endpoints"""
    print("\n=== Testing Family Endpoints ===")
    headers = {"Authorization": f"Token {token}"}
    
    # Get families
    response = requests.get(f"{BASE_URL}/families/", headers=headers)
    if response.status_code == 200:
        families_data = response.json()
        print(f"✅ Families response type: {type(families_data)}")
        
        # Handle both list and paginated response formats
        if isinstance(families_data, dict) and 'results' in families_data:
            families = families_data['results']
        else:
            families = families_data
            
        print(f"✅ Found {len(families)} families")
        
        if families:
            family_id = families[0]['id']
            print(f"Testing with family ID: {family_id}")
            
            # Get family members
            response = requests.get(f"{BASE_URL}/families/{family_id}/members/", headers=headers)
            if response.status_code == 200:
                members = response.json()
                print(f"✅ Found {len(members)} family members")
                
                # Test password reset endpoint (without actually resetting)
                print("\n--- Testing Password Reset Endpoint ---")
                test_data = {
                    "member_id": "test-id",
                    "new_password": "testpass123"
                }
                response = requests.patch(f"{BASE_URL}/families/{family_id}/reset-member-password/", 
                                        json=test_data, headers=headers)
                print(f"Password reset endpoint response: {response.status_code}")
                if response.status_code != 200:
                    print(f"Response: {response.text}")
                
                # Test remove member endpoint (without actually removing)
                print("\n--- Testing Remove Member Endpoint ---")
                test_data = {"member_id": "test-id"}
                response = requests.delete(f"{BASE_URL}/families/{family_id}/remove_member/", 
                                         json=test_data, headers=headers)
                print(f"Remove member endpoint response: {response.status_code}")
                if response.status_code != 200:
                    print(f"Response: {response.text}")
            else:
                print(f"❌ Failed to get family members: {response.status_code}")
    else:
        print(f"❌ Failed to get families: {response.status_code} - {response.text}")

def main():
    print("🔍 Debugging Authentication and Family Management Issues")
    print("=" * 60)
    
    # Test login
    token = test_login()
    if not token:
        return
    
    # Test family endpoints
    test_family_endpoints(token)
    
    # Test logout
    test_logout(token)

if __name__ == "__main__":
    main()