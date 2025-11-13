#!/usr/bin/env python3
"""
Test recipe update to debug 400 errors
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_recipe_update():
    """Test recipe update functionality"""
    print("=== Testing Recipe Update ===")
    
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
            headers = {"Authorization": f"Token {token}"}
            
            # Get recipes first
            response = requests.get(f"{BASE_URL}/recipes/", headers=headers)
            print(f"Get recipes: {response.status_code}")
            
            if response.status_code == 200:
                recipes_data = response.json()
                recipes = recipes_data.get('results', [])
                
                if recipes:
                    recipe_id = recipes[0]['id']
                    print(f"Testing with recipe: {recipe_id}")
                    
                    # Get the specific recipe
                    response = requests.get(f"{BASE_URL}/recipes/{recipe_id}/", headers=headers)
                    print(f"Get recipe detail: {response.status_code}")
                    
                    if response.status_code == 200:
                        recipe = response.json()
                        print(f"Recipe title: {recipe['title']}")
                        
                        # Try a simple update
                        update_data = {
                            "title": recipe['title'] + " (Updated)",
                            "description": recipe.get('description', '') + " Updated description.",
                            "prep_time": recipe.get('prep_time', 15),
                            "cook_time": recipe.get('cook_time', 20),
                            "servings": recipe.get('servings', 4),
                            "categories": recipe.get('categories', []),
                            "tags": recipe.get('tags', []),
                            "instructions": recipe.get('instructions', [])
                        }
                        
                        print("Attempting update...")
                        response = requests.put(f"{BASE_URL}/recipes/{recipe_id}/", 
                                              json=update_data, headers=headers)
                        print(f"Update response: {response.status_code}")
                        
                        if response.status_code != 200:
                            print(f"Error response: {response.text}")
                            
                            # Try with minimal data
                            print("Trying minimal update...")
                            minimal_data = {
                                "title": recipe['title']
                            }
                            
                            response = requests.patch(f"{BASE_URL}/recipes/{recipe_id}/", 
                                                    json=minimal_data, headers=headers)
                            print(f"Minimal update response: {response.status_code}")
                            
                            if response.status_code != 200:
                                print(f"Minimal update error: {response.text}")
                        else:
                            print("✅ Recipe update successful")
                    else:
                        print(f"Failed to get recipe detail: {response.text}")
                else:
                    print("No recipes found")
            else:
                print(f"Failed to get recipes: {response.text}")
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🔍 Testing Recipe Update Functionality")
    print("=" * 50)
    test_recipe_update()