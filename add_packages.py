import sys
import os
from uuid import uuid4
from datetime import datetime

# Add the app directory to the path
sys.path.append('app')

from app.utils.supabase_client import supabase

def create_default_packages():
    """Create default packages in the database"""
    
    # Default packages data
    default_packages = [
        {
            "id": str(uuid4()),
            "name": "Free",
            "description": "Perfect for getting started",
            "price": 0.00,
            "original_price": 0.00,
            "tier": "free",
            "is_active": True,
            "is_featured": False,
            "discount_percentage": 0,
            "storage_limit_gb": 1,
            "api_calls_per_month": 100,
            "max_users": 1,
            "support_level": "community",
            "features": ["1 GB Storage", "100 API calls/month", "Community support", "Basic analytics"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "Student",
            "description": "Special pricing for students",
            "price": 0.00,
            "original_price": 9.99,
            "tier": "student",
            "is_active": True,
            "is_featured": True,
            "discount_percentage": 100,
            "storage_limit_gb": 5,
            "api_calls_per_month": 1000,
            "max_users": 3,
            "support_level": "email",
            "features": ["5 GB Storage", "1,000 API calls/month", "Email support", "Advanced analytics"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "Freelancer",
            "description": "Great for independent professionals",
            "price": 19.99,
            "original_price": 29.99,
            "tier": "freelancer",
            "is_active": True,
            "is_featured": True,
            "discount_percentage": 33,
            "storage_limit_gb": 20,
            "api_calls_per_month": 5000,
            "max_users": 10,
            "support_level": "priority",
            "features": ["20 GB Storage", "5,000 API calls/month", "Priority support", "Advanced analytics"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    try:
        print("🔍 Checking existing packages...")
        
        # Check if packages already exist
        existing_response = supabase.table("packages").select("id").execute()
        
        if existing_response.data:
            print(f"✅ Found {len(existing_response.data)} existing packages")
            return
        
        print("📦 Creating default packages...")
        
        # Insert all packages
        for package in default_packages:
            print(f"  - Creating {package['name']} package...")
            response = supabase.table("packages").insert(package).execute()
            
            if response.data:
                print(f"    ✅ Created {package['name']} package")
            else:
                print(f"    ❌ Failed to create {package['name']} package")
        
        print("🎉 Default packages created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating packages: {e}")
        raise

if __name__ == "__main__":
    create_default_packages() 