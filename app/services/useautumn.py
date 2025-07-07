import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
import json

class UseAutumnService:
    def __init__(self):
        self.api_key = os.getenv("USEAUTUMN_API_KEY", "am_sk_test_UD6o9Z7vHCADk7MGFMPjQ01FtBvtDfShnqut2lmul1")
        self.base_url = os.getenv("USEAUTUMN_BASE_URL", "https://api.useautumn.com/v1")
        self.session = None
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def identify_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify user in UseAutumn system"""
        try:
            # Check if we have a real API key
            if self.api_key == "your_useautumn_api_key_here" or not self.api_key:
                # Mock mode - return success without API call
                print(f"🔧 Mock mode: User {user_id} identified in UseAutumn")
                return {
                    "success": True,
                    "message": "Mock mode - user identified",
                    "user_id": user_id
                }
            
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "userId": user_id,
                "email": user_data.get("email"),
                "name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                "metadata": {
                    "location": user_data.get("location"),
                    "persona": user_data.get("persona"),
                    "tier": user_data.get("tier"),
                    "income_level": user_data.get("income_level")
                }
            }
            
            async with session.post(
                f"{self.base_url}/identify",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"User identification failed: {response.status}")
                    return {"success": False, "error": "Identification failed"}
        except Exception as e:
            print(f"Error identifying user: {e}")
            return {"success": False, "error": str(e)}
    
    async def attach_product(self, user_id: str, product_id: str, success_url: str = None, cancel_url: str = None) -> Dict[str, Any]:
        """Generate Stripe Checkout URL for product purchase/upgrade"""
        try:
            # Check if we have a real API key
            if self.api_key == "your_useautumn_api_key_here" or not self.api_key:
                # Mock mode - return mock checkout URL
                print(f"🔧 Mock mode: Product {product_id} attached for user {user_id}")
                return {
                    "success": True,
                    "checkout_url": f"http://localhost:8000/mock-checkout?product={product_id}&user={user_id}",
                    "session_id": f"mock_session_{user_id}_{product_id}",
                    "message": "Mock mode - checkout URL generated"
                }
            
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "userId": user_id,
                "productId": product_id,
                "successUrl": success_url or f"/welcome/{user_id}?upgrade=success",
                "cancelUrl": cancel_url or f"/welcome/{user_id}?upgrade=cancelled"
            }
            
            async with session.post(
                f"{self.base_url}/attach",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "checkout_url": result.get("url"),
                        "session_id": result.get("sessionId")
                    }
                else:
                    print(f"Product attachment failed: {response.status}")
                    return {"success": False, "error": "Attachment failed"}
        except Exception as e:
            print(f"Error attaching product: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_entitlement(self, user_id: str, feature_id: str) -> Dict[str, Any]:
        """Check if user can access a specific feature"""
        try:
            # Check if we have a real API key
            if self.api_key == "your_useautumn_api_key_here" or not self.api_key:
                # Mock mode - return allowed for most features
                print(f"🔧 Mock mode: Checking entitlement for {feature_id}")
                return {
                    "allowed": True,
                    "limit": -1,  # Unlimited
                    "usage": 0,
                    "remaining": -1,
                    "message": "Mock mode - feature access granted"
                }
            
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "userId": user_id,
                "featureId": feature_id
            }
            
            async with session.post(
                f"{self.base_url}/check",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "allowed": result.get("allowed", False),
                        "limit": result.get("limit"),
                        "usage": result.get("usage"),
                        "remaining": result.get("remaining")
                    }
                else:
                    print(f"Entitlement check failed: {response.status}")
                    return {"allowed": False, "error": "Check failed"}
        except Exception as e:
            print(f"Error checking entitlement: {e}")
            return {"allowed": False, "error": str(e)}
    
    async def track_usage(self, user_id: str, feature_id: str, value: int = 1) -> Dict[str, Any]:
        """Track usage for billing purposes"""
        try:
            # Check if we have a real API key
            if self.api_key == "your_useautumn_api_key_here" or not self.api_key:
                # Mock mode - return success
                print(f"🔧 Mock mode: Tracking usage for {feature_id} - {value}")
                return {
                    "success": True,
                    "usage": value,
                    "limit": -1,
                    "remaining": -1,
                    "message": "Mock mode - usage tracked"
                }
            
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "userId": user_id,
                "featureId": feature_id,
                "value": value
            }
            
            async with session.post(
                f"{self.base_url}/track",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "usage": result.get("usage"),
                        "limit": result.get("limit"),
                        "remaining": result.get("remaining")
                    }
                else:
                    print(f"Usage tracking failed: {response.status}")
                    return {"success": False, "error": "Tracking failed"}
        except Exception as e:
            print(f"Error tracking usage: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_subscription(self, user_id: str) -> Dict[str, Any]:
        """Get user's current subscription details"""
        try:
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.get(
                f"{self.base_url}/subscriptions/{user_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Subscription fetch failed: {response.status}")
                    return {"error": "Subscription fetch failed"}
        except Exception as e:
            print(f"Error fetching subscription: {e}")
            return {"error": str(e)}
    
    def get_recommended_plan(self, user_data: Dict[str, Any]) -> str:
        """Get recommended plan based on user context"""
        email = user_data.get("email", "").lower()
        location = user_data.get("location", "").lower()
        job_title = user_data.get("job_title", "").lower()
        income_level = user_data.get("income_level", "unknown")
        
        # Students always get free plan
        if ".edu" in email or "student" in job_title:
            return "free_plan"
        
        # High-income users get premium
        if income_level in ["high", "very_high"] or any(title in job_title for title in ["ceo", "founder", "executive", "director"]):
            return "premium_plan"
        
        # Users from developing countries get fair plan
        if location in ["kenya", "uganda", "india", "nigeria", "ghana"]:
            return "fair_plan"
        
        # Default to fair plan for most users
        return "fair_plan"
    
    async def fetch_products(self) -> List[Dict[str, Any]]:
        """Fetch available products/plans from UseAutumn API"""
        try:
            if self.api_key == "your_useautumn_api_key_here" or not self.api_key:
                print(f"🔧 Mock mode: Returning empty product list")
                return []
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            async with session.get(f"{self.base_url}/plans", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to fetch products: {response.status}")
                    return []
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global UseAutumn service instance
useautumn_service = UseAutumnService() 