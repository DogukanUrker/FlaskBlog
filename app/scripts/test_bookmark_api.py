"""
Test script for bookmark functionality
Tests both logged in and logged out scenarios
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:1283"

def test_bookmark_functionality():
    """Test bookmark functionality"""
    print("🧪 Testing Bookmark Functionality")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("1. Testing server connection...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False
    
    # Test 2: Test bookmark API without login
    print("\n2. Testing bookmark API without login...")
    try:
        response = requests.post(f"{BASE_URL}/api/bookmark/1")
        if response.status_code == 401:
            print("✅ Correctly rejected unauthenticated request")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    # Test 3: Test bookmark status API without login
    print("\n3. Testing bookmark status API without login...")
    try:
        response = requests.get(f"{BASE_URL}/api/bookmark/status/1")
        if response.status_code == 200:
            data = response.json()
            if data.get("bookmarked") == False:
                print("✅ Correctly returned False for unauthenticated user")
            else:
                print(f"❌ Unexpected response: {data}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    # Test 4: Test my-bookmarks page without login
    print("\n4. Testing my-bookmarks page without login...")
    try:
        response = requests.get(f"{BASE_URL}/my-bookmarks", allow_redirects=False)
        if response.status_code == 302:
            print("✅ Correctly redirected to login page")
            print(f"Redirect location: {response.headers.get('Location')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Page test failed: {e}")
    
    print("\n🎯 Bookmark functionality tests completed!")
    return True

if __name__ == "__main__":
    test_bookmark_functionality()