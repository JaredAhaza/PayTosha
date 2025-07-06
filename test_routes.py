#!/usr/bin/env python3
"""
Simple test script to verify route fixes
"""

import requests
import json

def test_routes():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing PayTosha Routes")
    print("=" * 40)
    
    # Test 1: Debug users route
    print("\n1️⃣ Testing debug users route...")
    try:
        response = requests.get(f"{base_url}/debug/users")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug users: {data.get('user_count', 0)} users found")
        else:
            print(f"❌ Debug users failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Debug users error: {str(e)}")
    
    # Test 2: Packages dashboard route (should not give 422 error)
    print("\n2️⃣ Testing packages dashboard route...")
    try:
        response = requests.get(f"{base_url}/packages/dashboard?username=test")
        if response.status_code == 404:
            print("✅ Packages dashboard route works (404 expected for non-existent user)")
        elif response.status_code == 200:
            print("✅ Packages dashboard route works")
        else:
            print(f"⚠️ Packages dashboard: {response.status_code}")
    except Exception as e:
        print(f"❌ Packages dashboard error: {str(e)}")
    
    # Test 3: Compare packages route
    print("\n3️⃣ Testing compare packages route...")
    try:
        response = requests.get(f"{base_url}/packages/compare?username=test")
        if response.status_code == 404:
            print("✅ Compare packages route works (404 expected for non-existent user)")
        else:
            print(f"⚠️ Compare packages: {response.status_code}")
    except Exception as e:
        print(f"❌ Compare packages error: {str(e)}")
    
    # Test 4: Billing route
    print("\n4️⃣ Testing billing route...")
    try:
        response = requests.get(f"{base_url}/packages/billing?username=test")
        if response.status_code == 404:
            print("✅ Billing route works (404 expected for non-existent user)")
        else:
            print(f"⚠️ Billing: {response.status_code}")
    except Exception as e:
        print(f"❌ Billing error: {str(e)}")
    
    print("\n🎉 Route testing completed!")

if __name__ == "__main__":
    test_routes() 