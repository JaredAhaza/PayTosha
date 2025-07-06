import sys
import os
from uuid import uuid4
from datetime import datetime

# Add the app directory to the path
sys.path.append('app')

from app.utils.supabase_client import supabase

def add_sample_products():
    """Add sample products to the marketplace"""
    
    # Sample products data
    sample_products = [
        {
            "id": str(uuid4()),
            "name": "Complete Web Development Course",
            "description": "Learn HTML, CSS, JavaScript, and React from scratch. Perfect for beginners and intermediate developers.",
            "category": "Online Courses",
            "base_price": 99.99,
            "currency": "USD",
            "image_url": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=400",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "Professional Logo Design Package",
            "description": "Get a custom logo design with unlimited revisions, source files, and brand guidelines.",
            "category": "Services",
            "base_price": 299.99,
            "currency": "USD",
            "image_url": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "E-commerce Website Template",
            "description": "Responsive HTML/CSS template for online stores. Includes shopping cart and payment integration.",
            "category": "Digital Downloads",
            "base_price": 49.99,
            "currency": "USD",
            "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "Business Strategy Consultation",
            "description": "1-hour consultation with a business strategist to help grow your startup or small business.",
            "category": "Services",
            "base_price": 150.00,
            "currency": "USD",
            "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "Python Data Science Toolkit",
            "description": "Complete toolkit with Jupyter notebooks, datasets, and tutorials for data science projects.",
            "category": "Digital Downloads",
            "base_price": 79.99,
            "currency": "USD",
            "image_url": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "Premium Stock Photo Bundle",
            "description": "500 high-quality stock photos for commercial use. Perfect for websites and marketing materials.",
            "category": "Digital Downloads",
            "base_price": 29.99,
            "currency": "USD",
            "image_url": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=400",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    # Sample tier pricing data
    tier_pricing = [
        # Student discounts
        {"tier": "student", "price_multiplier": 0.5, "reasoning": "50% discount for students to support education"},
        {"tier": "freelancer", "price_multiplier": 0.75, "reasoning": "25% discount for freelancers and independent workers"},
        {"tier": "professional", "price_multiplier": 1.0, "reasoning": "Standard pricing for professionals"},
        {"tier": "enterprise", "price_multiplier": 1.25, "reasoning": "Premium pricing for enterprise customers with additional support"},
        {"tier": "free", "price_multiplier": 0.0, "reasoning": "Free access for users in need"}
    ]
    
    try:
        print("🔍 Checking existing products...")
        
        # Check if products already exist
        existing_response = supabase.table("products").select("id").execute()
        
        if existing_response.data:
            print(f"✅ Found {len(existing_response.data)} existing products")
            return
        
        print("📦 Creating sample products...")
        
        # Insert products
        created_products = []
        for product in sample_products:
            print(f"  - Creating {product['name']}...")
            response = supabase.table("products").insert(product).execute()
            
            if response.data:
                created_product = response.data[0]
                created_products.append(created_product)
                print(f"    ✅ Created product: {created_product['name']}")
                
                # Add tier pricing for this product
                for pricing in tier_pricing:
                    pricing_data = {
                        "id": str(uuid4()),
                        "product_id": created_product["id"],
                        "tier": pricing["tier"],
                        "price_multiplier": pricing["price_multiplier"],
                        "reasoning": pricing["reasoning"],
                        "is_active": True,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    
                    pricing_response = supabase.table("tier_pricing").insert(pricing_data).execute()
                    if pricing_response.data:
                        print(f"      ✅ Added {pricing['tier']} pricing")
                    else:
                        print(f"      ❌ Failed to add {pricing['tier']} pricing")
            else:
                print(f"    ❌ Failed to create {product['name']}")
        
        print(f"🎉 Created {len(created_products)} sample products with tier pricing!")
        
    except Exception as e:
        print(f"❌ Error creating products: {e}")
        raise

if __name__ == "__main__":
    add_sample_products() 