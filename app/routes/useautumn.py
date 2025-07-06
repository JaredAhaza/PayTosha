from fastapi import APIRouter, HTTPException, Request
from app.services.useautumn import useautumn_service
from app.utils.supabase_client import supabase
from typing import Dict, Any
import json

router = APIRouter(prefix="/useautumn", tags=["UseAutumn"])

@router.post("/identify/{user_id}")
async def identify_user(user_id: str, request: Request):
    """Identify user in UseAutumn system"""
    try:
        # Get user data from database
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        
        # Get context profile
        context_response = supabase.table("context_profiles").select("*").eq("user_id", user_id).execute()
        context_data = context_response.data[0] if context_response.data else {}
        
        # Combine user and context data
        full_user_data = {**user_data, **context_data}
        
        # Identify user in UseAutumn
        result = await useautumn_service.identify_user(user_id, full_user_data)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/attach/{user_id}/{product_id}")
async def attach_product(user_id: str, product_id: str, request: Request):
    """Generate Stripe Checkout URL for product purchase/upgrade"""
    try:
        data = await request.json()
        success_url = data.get("success_url")
        cancel_url = data.get("cancel_url")
        
        result = await useautumn_service.attach_product(user_id, product_id, success_url, cancel_url)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Attachment failed"))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check/{user_id}/{feature_id}")
async def check_entitlement(user_id: str, feature_id: str):
    """Check if user can access a specific feature"""
    try:
        result = await useautumn_service.check_entitlement(user_id, feature_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track/{user_id}/{feature_id}")
async def track_usage(user_id: str, feature_id: str, request: Request):
    """Track usage for billing purposes"""
    try:
        data = await request.json()
        value = data.get("value", 1)
        
        result = await useautumn_service.track_usage(user_id, feature_id, value)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscription/{user_id}")
async def get_subscription(user_id: str):
    """Get user's current subscription details"""
    try:
        result = await useautumn_service.get_user_subscription(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend-plan/{user_id}")
async def get_recommended_plan(user_id: str):
    """Get recommended plan based on user context"""
    try:
        # Get user data
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        
        # Get context profile
        context_response = supabase.table("context_profiles").select("*").eq("user_id", user_id).execute()
        context_data = context_response.data[0] if context_response.data else {}
        
        # Combine data
        full_user_data = {**user_data, **context_data}
        
        # Get recommended plan
        recommended_plan = useautumn_service.get_recommended_plan(full_user_data)
        plan_features = useautumn_service.get_plan_features(recommended_plan)
        
        return {
            "recommended_plan": recommended_plan,
            "plan_details": plan_features,
            "user_context": {
                "email": user_data.get("email"),
                "location": context_data.get("location"),
                "persona": context_data.get("persona"),
                "income_level": context_data.get("income_level")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans")
async def get_all_plans():
    """Get all available plans and their features"""
    try:
        return {
            "plans": useautumn_service.products,
            "features": {
                "basic_marketplace": "Access to basic marketplace features",
                "limited_crawls": "Limited social media crawling",
                "basic_analytics": "Basic usage analytics",
                "marketplace": "Full marketplace access",
                "social_crawls": "Social media profile crawling",
                "advanced_analytics": "Advanced analytics and insights",
                "fair_pricing": "Context-aware fair pricing",
                "unlimited_marketplace": "Unlimited marketplace access",
                "unlimited_crawls": "Unlimited social media crawling",
                "premium_analytics": "Premium analytics and reporting",
                "priority_support": "Priority customer support"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def handle_webhook(request: Request):
    """Handle UseAutumn webhooks for subscription events"""
    try:
        data = await request.json()
        event_type = data.get("type")
        
        # Handle different webhook events
        if event_type == "subscription.created":
            # New subscription created
            user_id = data.get("userId")
            product_id = data.get("productId")
            print(f"New subscription: User {user_id} subscribed to {product_id}")
            
        elif event_type == "subscription.updated":
            # Subscription updated
            user_id = data.get("userId")
            product_id = data.get("productId")
            print(f"Subscription updated: User {user_id} now has {product_id}")
            
        elif event_type == "subscription.cancelled":
            # Subscription cancelled
            user_id = data.get("userId")
            print(f"Subscription cancelled: User {user_id}")
            
        elif event_type == "usage.tracked":
            # Usage tracked
            user_id = data.get("userId")
            feature_id = data.get("featureId")
            usage = data.get("usage")
            print(f"Usage tracked: User {user_id} used {feature_id} - {usage}")
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 