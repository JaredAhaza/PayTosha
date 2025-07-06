from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import json
from app.utils.supabase_client import supabase
from app.schemas import Package, UserPackage, PackageWithSubscription, PackageComparison

class PackageService:
    def __init__(self):
        self.supabase = supabase
    
    async def get_all_packages(self, active_only: bool = True) -> List[Package]:
        """Get all available packages"""
        query = self.supabase.table("packages").select("*")
        if active_only:
            query = query.eq("is_active", True)
        
        response = query.order("price").execute()
        
        if response.data:
            return [Package(**package) for package in response.data]
        return []
    
    async def get_package_by_id(self, package_id: UUID) -> Optional[Package]:
        """Get a specific package by ID"""
        response = self.supabase.table("packages").select("*").eq("id", str(package_id)).execute()
        
        if response.data:
            return Package(**response.data[0])
        return None
    
    async def get_package_by_tier(self, tier: str) -> Optional[Package]:
        """Get package by tier name"""
        response = self.supabase.table("packages").select("*").eq("tier", tier).eq("is_active", True).execute()
        
        if response.data:
            return Package(**response.data[0])
        return None
    
    async def get_user_subscription(self, user_id: UUID) -> Optional[UserPackage]:
        """Get current user subscription"""
        response = self.supabase.table("user_packages").select("*, packages(*)").eq("user_id", str(user_id)).eq("status", "active").execute()
        
        if response.data:
            subscription_data = response.data[0]
            # Add package data to the subscription
            if 'packages' in subscription_data and subscription_data['packages']:
                subscription_data['package'] = subscription_data['packages']
            return UserPackage(**subscription_data)
        return None
    
    async def get_user_packages(self, user_id: UUID) -> List[UserPackage]:
        """Get all user packages (subscription history)"""
        response = self.supabase.table("user_packages").select("*, packages(*)").eq("user_id", str(user_id)).order("created_at", desc=True).execute()
        
        if response.data:
            packages = []
            for package_data in response.data:
                # Add package data to each subscription
                if 'packages' in package_data and package_data['packages']:
                    package_data['package'] = package_data['packages']
                packages.append(UserPackage(**package_data))
            return packages
        return []
    
    async def create_user_subscription(self, user_id: UUID, package_id: UUID, payment_method: str = None) -> UserPackage:
        """Create a new user subscription"""
        # Cancel any existing active subscription
        await self.cancel_user_subscription(user_id)
        
        # Get package details
        package = await self.get_package_by_id(package_id)
        if not package:
            raise ValueError("Package not found")
        
        # Calculate end date (30 days from now)
        end_date = datetime.utcnow() + timedelta(days=30)
        
        subscription_data = {
            "user_id": str(user_id),
            "package_id": str(package_id),
            "status": "active",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": end_date.isoformat(),
            "auto_renew": True,
            "payment_method": payment_method
        }
        
        response = self.supabase.table("user_packages").insert(subscription_data).execute()
        
        if response.data:
            return UserPackage(**response.data[0])
        raise Exception("Failed to create subscription")
    
    async def cancel_user_subscription(self, user_id: UUID) -> bool:
        """Cancel user's active subscription"""
        response = self.supabase.table("user_packages").update({"status": "cancelled"}).eq("user_id", str(user_id)).eq("status", "active").execute()
        return len(response.data) > 0
    
    async def update_subscription_auto_renew(self, user_id: UUID, auto_renew: bool) -> bool:
        """Update subscription auto-renewal setting"""
        response = self.supabase.table("user_packages").update({"auto_renew": auto_renew}).eq("user_id", str(user_id)).eq("status", "active").execute()
        return len(response.data) > 0
    
    async def get_packages_with_subscription_status(self, user_id: UUID) -> List[PackageWithSubscription]:
        """Get all packages with subscription status for a user"""
        packages = await self.get_all_packages()
        user_subscription = await self.get_user_subscription(user_id)
        
        packages_with_status = []
        for package in packages:
            is_subscribed = user_subscription and user_subscription.package_id == package.id
            can_upgrade = self._can_upgrade(package, user_subscription)
            can_downgrade = self._can_downgrade(package, user_subscription)
            
            package_with_status = PackageWithSubscription(
                **package.dict(),
                user_subscription=user_subscription if is_subscribed else None,
                is_subscribed=is_subscribed,
                can_upgrade=can_upgrade,
                can_downgrade=can_downgrade
            )
            packages_with_status.append(package_with_status)
        
        return packages_with_status
    
    async def get_package_comparison(self, user_id: UUID) -> PackageComparison:
        """Get package comparison for user"""
        packages = await self.get_all_packages()
        user_subscription = await self.get_user_subscription(user_id)
        
        current_package = None
        if user_subscription:
            current_package_data = await self.get_package_by_id(user_subscription.package_id)
            if current_package_data:
                current_package = PackageWithSubscription(
                    **current_package_data.dict(),
                    user_subscription=user_subscription,
                    is_subscribed=True,
                    can_upgrade=False,
                    can_downgrade=False
                )
        
        # Determine upgrade and downgrade paths
        upgrade_path = []
        downgrade_path = []
        
        if current_package:
            current_price = current_package.price
            for package in packages:
                if package.price > current_price:
                    upgrade_path.append(package)
                elif package.price < current_price:
                    downgrade_path.append(package)
            
            # Sort by price
            upgrade_path.sort(key=lambda x: x.price)
            downgrade_path.sort(key=lambda x: x.price, reverse=True)
        
        # Recommend next tier up if available
        recommended_package = None
        if upgrade_path:
            recommended_package = upgrade_path[0]
        
        return PackageComparison(
            current_package=current_package,
            available_packages=packages,
            recommended_package=recommended_package,
            upgrade_path=upgrade_path,
            downgrade_path=downgrade_path
        )
    
    async def get_usage_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's current usage statistics"""
        user_subscription = await self.get_user_subscription(user_id)
        if not user_subscription:
            return {"error": "No active subscription"}
        
        package = await self.get_package_by_id(user_subscription.package_id)
        if not package:
            return {"error": "Package not found"}
        
        # Mock usage data - in real app, this would come from actual usage tracking
        usage_data = {
            "api_calls_used": 0,  # Would be calculated from actual API usage
            "api_calls_limit": package.api_calls_per_month,
            "storage_used_gb": 0.1,  # Would be calculated from actual storage
            "storage_limit_gb": package.storage_limit_gb,
            "users_count": 1,  # Would be calculated from actual user count
            "users_limit": package.max_users,
            "subscription_start": user_subscription.start_date,
            "subscription_end": user_subscription.end_date,
            "auto_renew": user_subscription.auto_renew,
            "days_remaining": (user_subscription.end_date - datetime.utcnow()).days if user_subscription.end_date else 0
        }
        
        return usage_data
    
    def _can_upgrade(self, package: Package, user_subscription: Optional[UserPackage]) -> bool:
        """Check if user can upgrade to this package"""
        if not user_subscription:
            return True
        
        # Get current package price
        current_package = self._get_package_by_id_sync(user_subscription.package_id)
        if not current_package:
            return True
        
        return package.price > current_package.price
    
    def _can_downgrade(self, package: Package, user_subscription: Optional[UserPackage]) -> bool:
        """Check if user can downgrade to this package"""
        if not user_subscription:
            return False
        
        # Get current package price
        current_package = self._get_package_by_id_sync(user_subscription.package_id)
        if not current_package:
            return False
        
        return package.price < current_package.price
    
    def _get_package_by_id_sync(self, package_id: UUID) -> Optional[Package]:
        """Synchronous version of get_package_by_id for internal use"""
        response = self.supabase.table("packages").select("*").eq("id", str(package_id)).execute()
        
        if response.data:
            return Package(**response.data[0])
        return None
    
    def get_package_by_tier_sync(self, tier: str) -> Optional[Package]:
        """Synchronous version of get_package_by_tier for internal use"""
        response = self.supabase.table("packages").select("*").eq("tier", tier).eq("is_active", True).execute()
        
        if response.data:
            return Package(**response.data[0])
        return None
    
    async def get_featured_packages(self) -> List[Package]:
        """Get featured packages (those with discounts or special offers)"""
        response = self.supabase.table("packages").select("*").gt("discount_percentage", 0).eq("is_active", True).order("discount_percentage", desc=True).execute()
        
        if response.data:
            return [Package(**package) for package in response.data]
        return []
    
    async def search_packages(self, query: str) -> List[Package]:
        """Search packages by name or description"""
        response = self.supabase.table("packages").select("*").or_(f"name.ilike.%{query}%,description.ilike.%{query}%").eq("is_active", True).execute()
        
        if response.data:
            return [Package(**package) for package in response.data]
        return [] 