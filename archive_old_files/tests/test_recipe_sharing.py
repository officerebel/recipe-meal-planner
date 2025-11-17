#!/usr/bin/env python
"""
Test script for recipe sharing functionality
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
RECIPE_ID = "9c8c1589-bbaf-4faa-b585-c4307e7b500d"

def get_auth_token(username, password):
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login/", json={
        "email": username,
        "password": password
    })
    
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_recipe_sharing():
    """Test recipe sharing functionality"""
    print("🧪 Testing Recipe Sharing API")
    print("=" * 40)
    
    # Login as admin user
    token = get_auth_token("admin@example.com", "admin123")
    if not token:
        return
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    print(f"✅ Logged in successfully")
    
    # Test 1: Get current recipe details
    print(f"\n📋 Testing recipe access...")
    response = requests.get(f"{BASE_URL}/api/recipes/{RECIPE_ID}/", headers=headers)
    
    if response.status_code == 200:
        recipe = response.json()
        print(f"✅ Recipe found: {recipe['title'][:50]}...")
        print(f"   Owner: {recipe.get('user', 'Unknown')}")
        print(f"   Shared with family: {recipe.get('is_shared_with_family', False)}")
    else:
        print(f"❌ Failed to get recipe: {response.status_code} - {response.text}")
        return
    
    # Test 2: Share recipe with family
    print(f"\n🔗 Testing recipe sharing...")
    response = requests.post(
        f"{BASE_URL}/api/recipes/{RECIPE_ID}/share-with-family/",
        headers=headers,
        json={"share": True}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Share successful: {result['message']}")
        print(f"   Shared status: {result['is_shared_with_family']}")
    else:
        print(f"❌ Share failed: {response.status_code} - {response.text}")
    
    # Test 3: Check family recipes
    print(f"\n👨‍👩‍👧‍👦 Testing family recipes view...")
    response = requests.get(f"{BASE_URL}/api/recipes/?scope=family", headers=headers)
    
    if response.status_code == 200:
        recipes = response.json()
        count = recipes.get('count', len(recipes.get('results', recipes)))
        print(f"✅ Family recipes found: {count}")
        
        if isinstance(recipes, dict) and 'results' in recipes:
            for recipe in recipes['results'][:3]:  # Show first 3
                print(f"   - {recipe['title'][:40]}... (by {recipe.get('user', 'Unknown')})")
    else:
        print(f"❌ Failed to get family recipes: {response.status_code} - {response.text}")
    
    # Test 4: Check personal recipes
    print(f"\n👤 Testing personal recipes view...")
    response = requests.get(f"{BASE_URL}/api/recipes/?scope=personal", headers=headers)
    
    if response.status_code == 200:
        recipes = response.json()
        count = recipes.get('count', len(recipes.get('results', recipes)))
        print(f"✅ Personal recipes found: {count}")
    else:
        print(f"❌ Failed to get personal recipes: {response.status_code} - {response.text}")
    
    # Test 5: Unshare recipe
    print(f"\n🔓 Testing recipe unsharing...")
    response = requests.post(
        f"{BASE_URL}/api/recipes/{RECIPE_ID}/share-with-family/",
        headers=headers,
        json={"share": False}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Unshare successful: {result['message']}")
        print(f"   Shared status: {result['is_shared_with_family']}")
    else:
        print(f"❌ Unshare failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_recipe_sharing()