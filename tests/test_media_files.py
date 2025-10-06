#!/usr/bin/env python3
"""
Test media file serving on Railway
"""
import requests

API_BASE = "https://proud-mercy-production.up.railway.app"

def test_media_serving():
    """Test if media files are being served correctly"""
    print("🧪 Testing Media File Serving...")
    
    # Test a known media file from the logs
    media_files = [
        "/media/recipe_images/Schermafbeelding_2025-10-05_om_14.46.24.png",
        "/media/recipe_images/Schermafbeelding_2025-10-05_om_14.58.24.png"
    ]
    
    for media_file in media_files:
        try:
            print(f"\n📁 Testing: {media_file}")
            response = requests.get(f"{API_BASE}{media_file}")
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            
            if response.status_code == 404:
                print("❌ File not found (404)")
            elif response.status_code == 200:
                print("✅ File served successfully")
                print(f"📏 Content Length: {len(response.content)} bytes")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
    
    # Test the media directory endpoint
    print(f"\n📁 Testing media directory access...")
    try:
        response = requests.get(f"{API_BASE}/media/")
        print(f"📊 Media directory status: {response.status_code}")
        if response.status_code == 404:
            print("❌ Media directory not accessible")
        elif response.status_code == 403:
            print("⚠️ Media directory access forbidden (normal)")
        else:
            print(f"📄 Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Media directory test failed: {e}")

if __name__ == "__main__":
    test_media_serving()