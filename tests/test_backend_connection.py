#!/usr/bin/env python3
"""
Test script to check backend connection and create sample data
"""

import requests
import json

# Backend URL
BACKEND_URL = "https://proud-mercy-production.up.railway.app"

def test_backend_connection():
    """Test if backend is accessible"""
    try:
        print("🔍 Testing backend connection...")
        response = requests.get(f"{BACKEND_URL}/api/health/", timeout=10)
        print(f"✅ Backend health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_recipes_endpoint():
    """Test recipes endpoint"""
    try:
        print("\n🔍 Testing recipes endpoint...")
        response = requests.get(f"{BACKEND_URL}/api/recipes/", timeout=10)
        print(f"   Recipes endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('results', []))} recipes")
            return data
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Recipes endpoint failed: {e}")
        return None

def test_specific_recipe(recipe_id):
    """Test specific recipe endpoint"""
    try:
        print(f"\n🔍 Testing specific recipe: {recipe_id}")
        response = requests.get(f"{BACKEND_URL}/api/recipes/{recipe_id}/", timeout=10)
        print(f"   Recipe detail: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Recipe: {data.get('title', 'Unknown')}")
            return data
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Recipe detail failed: {e}")
        return None

def main():
    print("🚀 Backend Connection Test")
    print("=" * 50)
    
    # Test backend connection
    if not test_backend_connection():
        print("\n❌ Backend is not accessible. Check Railway deployment.")
        return
    
    # Test recipes endpoint
    recipes_data = test_recipes_endpoint()
    
    # Test the specific recipe that's giving 404
    recipe_id = "4cc40e84-050f-479b-a4c5-c42e212a40bf"
    test_specific_recipe(recipe_id)
    
    # Show available recipes
    if recipes_data and recipes_data.get('results'):
        print(f"\n📋 Available recipes:")
        for recipe in recipes_data['results'][:5]:  # Show first 5
            print(f"   - {recipe.get('title', 'Unknown')} (ID: {recipe.get('id', 'Unknown')})")
    else:
        print("\n⚠️  No recipes found. You may need to create sample data.")
        print("\n💡 Suggestions:")
        print("   1. Login to the app and create some recipes")
        print("   2. Or run the sample data creation command on Railway")

if __name__ == "__main__":
    main()