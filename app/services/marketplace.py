from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import json
from app.utils.supabase_client import supabase
from app.schemas import Product, ProductCategory, TierPricing, ProductWithPricing, Order, ProductCreate, TierPricingCreate, OrderCreate

class MarketplaceService:
    def __init__(self):
        self.supabase = supabase
    
    async def get_all_categories(self) -> List[ProductCategory]:
        """Get all product categories"""
        response = self.supabase.table("product_categories").select("*").eq("is_active", True).execute()
        
        if response.data:
            return [ProductCategory(**category) for category in response.data]
        return []
    
    async def get_all_products(self, category_id: Optional[UUID] = None) -> List[Product]:
        """Get all active products, optionally filtered by category"""
        query = self.supabase.table("products").select("*").eq("is_active", True)
        
        if category_id:
            query = query.eq("category_id", str(category_id))
        
        response = query.order("created_at", desc=True).execute()
        
        if response.data:
            return [Product(**product) for product in response.data]
        return []
    
    async def get_product_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get a specific product by ID"""
        response = self.supabase.table("products").select("*").eq("id", str(product_id)).execute()
        
        if response.data:
            return Product(**response.data[0])
        return None
    
    async def get_product_with_pricing(self, product_id: UUID, user_tier: Optional[str] = None) -> Optional[ProductWithPricing]:
        """Get product with tier pricing and calculate user-specific price"""
        # Get product
        product = await self.get_product_by_id(product_id)
        if not product:
            return None
        
        # Get tier pricing
        response = self.supabase.table("tier_pricing").select("*").eq("product_id", str(product_id)).eq("is_active", True).execute()
        tier_pricing = [TierPricing(**tp) for tp in response.data] if response.data else []
        
        # Calculate user-specific price
        user_price = None
        fairness_reasoning = None
        
        if user_tier:
            user_tier_pricing = next((tp for tp in tier_pricing if tp.tier == user_tier), None)
            if user_tier_pricing:
                if user_tier_pricing.fixed_price:
                    user_price = user_tier_pricing.fixed_price
                    fairness_reasoning = user_tier_pricing.reasoning or f"Fixed price for {user_tier} tier"
                else:
                    user_price = product.base_price * user_tier_pricing.price_multiplier
                    fairness_reasoning = user_tier_pricing.reasoning or f"{user_tier_pricing.price_multiplier}x multiplier for {user_tier} tier"
            else:
                # Default to base price if no specific tier pricing
                user_price = product.base_price
                fairness_reasoning = f"Standard pricing for {user_tier} tier"
        
        return ProductWithPricing(
            product=product,
            tier_pricing=tier_pricing,
            user_tier=user_tier,
            user_price=user_price,
            fairness_reasoning=fairness_reasoning
        )
    
    async def create_product(self, product_data: ProductCreate, created_by: UUID) -> Product:
        """Create a new product"""
        product_dict = product_data.dict()
        product_dict["created_by"] = str(created_by)
        
        response = self.supabase.table("products").insert(product_dict).execute()
        
        if response.data:
            return Product(**response.data[0])
        raise Exception("Failed to create product")
    
    async def add_tier_pricing(self, product_id: UUID, tier_pricing_data: TierPricingCreate) -> TierPricing:
        """Add tier pricing for a product"""
        pricing_dict = tier_pricing_data.dict()
        pricing_dict["product_id"] = str(product_id)
        
        response = self.supabase.table("tier_pricing").insert(pricing_dict).execute()
        
        if response.data:
            return TierPricing(**response.data[0])
        raise Exception("Failed to add tier pricing")
    
    async def create_order(self, order_data: OrderCreate, user_id: UUID, user_tier: str) -> Order:
        """Create a new order with fair pricing"""
        # Get product with pricing
        product_with_pricing = await self.get_product_with_pricing(order_data.product_id, user_tier)
        if not product_with_pricing:
            raise ValueError("Product not found")
        
        # Calculate final price
        original_price = product_with_pricing.product.base_price
        final_price = product_with_pricing.user_price or original_price
        
        order_dict = {
            "user_id": str(user_id),
            "product_id": str(order_data.product_id),
            "tier": user_tier,
            "original_price": float(original_price),
            "final_price": float(final_price),
            "currency": product_with_pricing.product.currency,
            "payment_method": order_data.payment_method,
            "fairness_reasoning": product_with_pricing.fairness_reasoning
        }
        
        response = self.supabase.table("orders").insert(order_dict).execute()
        
        if response.data:
            return Order(**response.data[0])
        raise Exception("Failed to create order")
    
    async def get_user_orders(self, user_id: UUID) -> List[Order]:
        """Get all orders for a user"""
        response = self.supabase.table("orders").select("*, products(*)").eq("user_id", str(user_id)).order("created_at", desc=True).execute()
        
        if response.data:
            orders = []
            for order_data in response.data:
                # Add product data to order
                if 'products' in order_data and order_data['products']:
                    order_data['product'] = order_data['products']
                orders.append(Order(**order_data))
            return orders
        return []
    
    async def get_products_by_category(self, category_id: UUID) -> List[Product]:
        """Get products filtered by category"""
        return await self.get_all_products(category_id)
    
    async def search_products(self, query: str) -> List[Product]:
        """Search products by name or description"""
        response = self.supabase.table("products").select("*").eq("is_active", True).or_(f"name.ilike.%{query}%,description.ilike.%{query}%").execute()
        
        if response.data:
            return [Product(**product) for product in response.data]
        return []
    
    async def get_featured_products(self, user_tier: Optional[str] = None) -> List[ProductWithPricing]:
        """Get featured products with user-specific pricing"""
        # For now, get recent products as featured
        response = self.supabase.table("products").select("*").eq("is_active", True).order("created_at", desc=True).limit(6).execute()
        
        if response.data:
            featured_products = []
            for product_data in response.data:
                product = Product(**product_data)
                product_with_pricing = await self.get_product_with_pricing(product.id, user_tier)
                if product_with_pricing:
                    featured_products.append(product_with_pricing)
            return featured_products
        return []
    
    def calculate_fair_price(self, base_price: Decimal, user_tier: str, tier_pricing: List[TierPricing]) -> tuple[Decimal, str]:
        """Calculate fair price for a user based on their tier"""
        user_tier_pricing = next((tp for tp in tier_pricing if tp.tier == user_tier), None)
        
        if user_tier_pricing:
            if user_tier_pricing.fixed_price:
                return user_tier_pricing.fixed_price, user_tier_pricing.reasoning or f"Fixed price for {user_tier} tier"
            else:
                final_price = base_price * user_tier_pricing.price_multiplier
                return final_price, user_tier_pricing.reasoning or f"{user_tier_pricing.price_multiplier}x multiplier for {user_tier} tier"
        
        # Default pricing logic based on tier
        tier_multipliers = {
            "free": Decimal("0.00"),
            "student": Decimal("0.50"),
            "freelancer": Decimal("0.75"),
            "professional": Decimal("1.00"),
            "enterprise": Decimal("1.25")
        }
        
        multiplier = tier_multipliers.get(user_tier, Decimal("1.00"))
        final_price = base_price * multiplier
        
        reasoning = f"Standard {user_tier} tier pricing ({multiplier}x base price)"
        
        return final_price, reasoning 