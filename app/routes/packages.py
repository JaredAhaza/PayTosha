from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from uuid import UUID
import json

from app.services.packages import PackageService
from app.schemas import Package, UserPackage, PackageWithSubscription, PackageComparison, UserPackageCreate, UserPackageUpdate
from app.utils.security import get_current_user_from_session
from app.utils.supabase_client import supabase

router = APIRouter(prefix="/packages", tags=["packages"])
templates = Jinja2Templates(directory="app/templates")
package_service = PackageService()

# 🔹 API Routes

@router.get("/", response_model=List[Package])
async def get_all_packages(active_only: bool = True):
    """Get all available packages"""
    return await package_service.get_all_packages(active_only)

@router.get("/featured", response_model=List[Package])
async def get_featured_packages():
    """Get featured packages (with discounts)"""
    return await package_service.get_featured_packages()

# Move this route after the specific named routes to avoid conflicts
# @router.get("/{package_id}", response_model=Package)
# async def get_package(package_id: UUID):
#     """Get a specific package by ID"""
#     package = await package_service.get_package_by_id(package_id)
#     if not package:
#         raise HTTPException(status_code=404, detail="Package not found")
#     return package

@router.get("/tier/{tier}", response_model=Package)
async def get_package_by_tier(tier: str):
    """Get package by tier name"""
    package = await package_service.get_package_by_tier(tier)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@router.get("/user/subscription", response_model=Optional[UserPackage])
async def get_user_subscription(request: Request, user_id: UUID = Depends(get_current_user_from_session)):
    """Get current user's subscription"""
    return await package_service.get_user_subscription(user_id)

@router.get("/user/history", response_model=List[UserPackage])
async def get_user_package_history(request: Request, user_id: UUID = Depends(get_current_user_from_session)):
    """Get user's package subscription history"""
    return await package_service.get_user_packages(user_id)

@router.post("/subscribe", response_model=UserPackage)
async def subscribe_to_package(
    subscription: UserPackageCreate,
    request: Request,
    user_id: UUID = Depends(get_current_user_from_session)
):
    """Subscribe to a package"""
    try:
        return await package_service.create_user_subscription(
            user_id=user_id,
            package_id=subscription.package_id,
            payment_method=subscription.payment_method
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create subscription")

@router.put("/subscription/cancel")
async def cancel_subscription(request: Request, user_id: UUID = Depends(get_current_user_from_session)):
    """Cancel current subscription"""
    success = await package_service.cancel_user_subscription(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return {"message": "Subscription cancelled successfully"}

@router.put("/subscription/auto-renew")
async def update_auto_renew(
    auto_renew: bool,
    request: Request,
    user_id: UUID = Depends(get_current_user_from_session)
):
    """Update subscription auto-renewal setting"""
    success = await package_service.update_subscription_auto_renew(user_id, auto_renew)
    if not success:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return {"message": "Auto-renewal setting updated successfully"}

@router.get("/user/usage", response_model=dict)
async def get_usage_stats(request: Request, user_id: UUID = Depends(get_current_user_from_session)):
    """Get user's current usage statistics"""
    return await package_service.get_usage_stats(user_id)

@router.get("/comparison", response_model=PackageComparison)
async def get_package_comparison(request: Request, user_id: UUID = Depends(get_current_user_from_session)):
    """Get package comparison for current user"""
    return await package_service.get_package_comparison(user_id)

@router.get("/search/{query}", response_model=List[Package])
async def search_packages(query: str):
    """Search packages by name or description"""
    return await package_service.search_packages(query)

@router.get("/debug")
async def debug_packages():
    """Debug endpoint to check packages data"""
    try:
        package_service = PackageService()
        packages = await package_service.get_all_packages()
        print(f"🔍 Debug: Found {len(packages)} packages")
        for p in packages:
            print(f"  - {p.name}: ${p.price} ({p.tier})")
        return {"packages_count": len(packages), "packages": [p.dict() for p in packages]}
    except Exception as e:
        print(f"❌ Debug error: {e}")
        return {"error": str(e)}

@router.get("/create-default")
async def create_default_packages():
    """Create default packages in the database"""
    try:
        from uuid import uuid4
        from datetime import datetime
        
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
        
        # Check if packages already exist
        existing_response = supabase.table("packages").select("id").execute()
        
        if existing_response.data:
            return {"message": f"Found {len(existing_response.data)} existing packages", "packages": existing_response.data}
        
        # Insert all packages
        created_packages = []
        for package in default_packages:
            response = supabase.table("packages").insert(package).execute()
            if response.data:
                created_packages.append(response.data[0])
        
        return {"message": f"Created {len(created_packages)} packages", "packages": created_packages}
        
    except Exception as e:
        print(f"❌ Error creating packages: {e}")
        return {"error": str(e)}

# 🔹 Frontend Routes

@router.get("/dashboard", response_class=HTMLResponse)
async def packages_dashboard(request: Request, username: str):
    """Packages dashboard page"""
    try:
        print(f"🔍 Packages dashboard - Looking for user: '{username}'")
        
        # Get user data by username (case-insensitive)
        username_lower = username.lower()
        user_response = supabase.table("users").select("*").eq("username", username_lower).execute()
        
        if not user_response.data:
            # Try original case
            user_response = supabase.table("users").select("*").eq("username", username).execute()
            
        if not user_response.data:
            # Try case-insensitive search
            user_response = supabase.table("users").select("*").ilike("username", f"%{username}%").execute()
            
        if not user_response.data:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
            
        user = user_response.data[0]
        user_id = UUID(user["id"])
        print(f"✅ Found user: {user['username']} with ID: {user_id}")
        
        # Get packages with subscription status
        print(f"🔍 Getting packages with subscription status for user {user_id}")
        try:
            packages_with_status = await package_service.get_packages_with_subscription_status(user_id)
            print(f"✅ Found {len(packages_with_status)} packages")
        except Exception as e:
            print(f"❌ Error getting packages: {e}")
            packages_with_status = []
        
        # Get current subscription
        print(f"🔍 Getting current subscription for user {user_id}")
        try:
            current_subscription = await package_service.get_user_subscription(user_id)
            print(f"✅ Current subscription: {current_subscription.package.name if current_subscription and current_subscription.package else 'None'}")
        except Exception as e:
            print(f"❌ Error getting subscription: {e}")
            current_subscription = None
        
        # Get usage stats
        print(f"🔍 Getting usage stats for user {user_id}")
        try:
            usage_stats = await package_service.get_usage_stats(user_id)
            print(f"✅ Usage stats: {usage_stats}")
        except Exception as e:
            print(f"❌ Error getting usage stats: {e}")
            usage_stats = {"error": "Unable to load usage stats"}
        
        # Get package comparison
        print(f"🔍 Getting package comparison for user {user_id}")
        try:
            comparison = await package_service.get_package_comparison(user_id)
            print(f"✅ Package comparison ready")
        except Exception as e:
            print(f"❌ Error getting comparison: {e}")
            comparison = None
        
        # Get featured packages
        print(f"🔍 Getting featured packages")
        try:
            featured_packages = await package_service.get_featured_packages()
            print(f"✅ Found {len(featured_packages)} featured packages")
        except Exception as e:
            print(f"❌ Error getting featured packages: {e}")
            featured_packages = []
        
        context = {
            "request": request,
            "user": user,
            "packages": packages_with_status,
            "current_subscription": current_subscription,
            "usage_stats": usage_stats,
            "comparison": comparison,
            "featured_packages": featured_packages,
            "active_tab": "packages"
        }
        
        return templates.TemplateResponse("packages_dashboard.html", context)
        
    except Exception as e:
        print(f"❌ Packages dashboard error: {str(e)}")
        context = {
            "request": request,
            "error": str(e),
            "active_tab": "packages",
            "user": {"username": "unknown"},  # Provide fallback user data
            "packages": [],
            "current_subscription": None,
            "usage_stats": {},
            "comparison": None,
            "featured_packages": []
        }
        return templates.TemplateResponse("packages_dashboard.html", context)

@router.get("/compare", response_class=HTMLResponse)
async def compare_packages(request: Request, username: str):
    """Package comparison page"""
    try:
        # Get user data by username (case-insensitive)
        username_lower = username.lower()
        user_response = supabase.table("users").select("*").eq("username", username_lower).execute()
        
        if not user_response.data:
            user_response = supabase.table("users").select("*").eq("username", username).execute()
            
        if not user_response.data:
            user_response = supabase.table("users").select("*").ilike("username", f"%{username}%").execute()
            
        if not user_response.data:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
            
        user = user_response.data[0]
        user_id = UUID(user["id"])
        
        comparison = await package_service.get_package_comparison(user_id)
        
        context = {
            "request": request,
            "comparison": comparison,
            "active_tab": "packages"
        }
        
        return templates.TemplateResponse("package_comparison.html", context)
        
    except Exception as e:
        context = {
            "request": request,
            "error": str(e),
            "active_tab": "packages",
            "user": {"username": "unknown"},  # Provide fallback user data
            "comparison": None
        }
        return templates.TemplateResponse("package_comparison.html", context)

@router.get("/billing", response_class=HTMLResponse)
async def billing_page(request: Request, username: str):
    """Billing and subscription management page"""
    try:
        # Get user data by username (case-insensitive)
        username_lower = username.lower()
        user_response = supabase.table("users").select("*").eq("username", username_lower).execute()
        
        if not user_response.data:
            user_response = supabase.table("users").select("*").eq("username", username).execute()
            
        if not user_response.data:
            user_response = supabase.table("users").select("*").ilike("username", f"%{username}%").execute()
            
        if not user_response.data:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
            
        user = user_response.data[0]
        user_id = UUID(user["id"])
        
        # Get user subscription history
        subscription_history = await package_service.get_user_packages(user_id)
        
        # Get current subscription
        current_subscription = await package_service.get_user_subscription(user_id)
        
        # Get usage stats
        usage_stats = await package_service.get_usage_stats(user_id)
        
        context = {
            "request": request,
            "subscription_history": subscription_history,
            "current_subscription": current_subscription,
            "usage_stats": usage_stats,
            "active_tab": "packages"
        }
        
        return templates.TemplateResponse("billing.html", context)
        
    except Exception as e:
        context = {
            "request": request,
            "error": str(e),
            "active_tab": "packages",
            "user": {"username": "unknown"},  # Provide fallback user data
            "subscription_history": [],
            "current_subscription": None,
            "usage_stats": {}
        }
        return templates.TemplateResponse("billing.html", context)

# 🔹 API Routes (moved to end to avoid conflicts)

@router.get("/{package_id}", response_model=Package)
async def get_package(package_id: UUID):
    """Get a specific package by ID"""
    package = await package_service.get_package_by_id(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package 