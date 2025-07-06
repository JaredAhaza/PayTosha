from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from uuid import UUID
import json

from app.services.marketplace import MarketplaceService
from app.schemas import Product, ProductCategory, ProductWithPricing, Order, ProductCreate, TierPricingCreate, OrderCreate
from app.utils.security import get_current_user_from_session
from app.utils.supabase_client import supabase

router = APIRouter(prefix="/marketplace", tags=["marketplace"])
templates = Jinja2Templates(directory="app/templates")
marketplace_service = MarketplaceService()

# 🔹 API Routes

@router.get("/categories", response_model=List[ProductCategory])
async def get_categories():
    """Get all product categories"""
    return await marketplace_service.get_all_categories()

@router.get("/products", response_model=List[Product])
async def get_products(category_id: Optional[UUID] = None):
    """Get all products, optionally filtered by category"""
    return await marketplace_service.get_all_products(category_id)

@router.get("/products/{product_id}", response_model=ProductWithPricing)
async def get_product(product_id: UUID, user_tier: Optional[str] = None):
    """Get a specific product with tier pricing"""
    product = await marketplace_service.get_product_with_pricing(product_id, user_tier)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=Product)
async def create_product(
    product_data: ProductCreate,
    request: Request,
    user_id: UUID = Depends(get_current_user_from_session)
):
    """Create a new product (admin/vendor only)"""
    try:
        return await marketplace_service.create_product(product_data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{product_id}/pricing", response_model=ProductWithPricing)
async def add_tier_pricing(
    product_id: UUID,
    pricing_data: TierPricingCreate,
    request: Request,
    user_id: UUID = Depends(get_current_user_from_session)
):
    """Add tier pricing for a product"""
    try:
        await marketplace_service.add_tier_pricing(product_id, pricing_data)
        return await marketplace_service.get_product_with_pricing(product_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders", response_model=Order)
async def create_order(
    order_data: OrderCreate,
    request: Request,
    user_id: UUID = Depends(get_current_user_from_session)
):
    """Create a new order with fair pricing"""
    try:
        # Get user's tier from context profile
        user_response = supabase.table("context_profiles").select("tier_suggestion").eq("user_id", str(user_id)).execute()
        user_tier = "professional"  # default
        if user_response.data:
            user_tier = user_response.data[0].get("tier_suggestion", "professional")
        
        return await marketplace_service.create_order(order_data, user_id, user_tier)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/orders", response_model=List[Order])
async def get_user_orders(request: Request, user_id: UUID = Depends(get_current_user_from_session)):
    """Get current user's orders"""
    return await marketplace_service.get_user_orders(user_id)

@router.get("/search/{query}", response_model=List[Product])
async def search_products(query: str):
    """Search products by name or description"""
    return await marketplace_service.search_products(query)

# 🔹 Frontend Routes

@router.get("/", response_class=HTMLResponse)
async def marketplace_home(request: Request, username: str):
    """Marketplace home page with featured products"""
    try:
        # Get user data
        user_response = supabase.table("users").select("*").eq("username", username.lower()).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_response.data[0]
        user_id = UUID(user["id"])
        
        # Get user's tier
        context_response = supabase.table("context_profiles").select("tier_suggestion").eq("user_id", str(user_id)).execute()
        user_tier = "professional"  # default
        if context_response.data:
            user_tier = context_response.data[0].get("tier_suggestion", "professional")
        
        # Get marketplace data
        categories = await marketplace_service.get_all_categories()
        featured_products = await marketplace_service.get_featured_products(user_tier)
        recent_products = await marketplace_service.get_all_products()
        
        context = {
            "request": request,
            "user": user,
            "user_tier": user_tier,
            "categories": categories,
            "featured_products": featured_products,
            "recent_products": recent_products[:8],  # Show 8 recent products
            "active_tab": "marketplace"
        }
        
        return templates.TemplateResponse("marketplace.html", context)
        
    except Exception as e:
        print(f"❌ Marketplace error: {str(e)}")
        context = {
            "request": request,
            "error": str(e),
            "active_tab": "marketplace",
            "user": {"username": "unknown"},
            "categories": [],
            "featured_products": [],
            "recent_products": []
        }
        return templates.TemplateResponse("marketplace.html", context)

@router.get("/category/{category_id}", response_class=HTMLResponse)
async def category_products(request: Request, category_id: UUID, username: str):
    """Products filtered by category"""
    try:
        # Get user data
        user_response = supabase.table("users").select("*").eq("username", username.lower()).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_response.data[0]
        user_id = UUID(user["id"])
        
        # Get user's tier
        context_response = supabase.table("context_profiles").select("tier_suggestion").eq("user_id", str(user_id)).execute()
        user_tier = "professional"
        if context_response.data:
            user_tier = context_response.data[0].get("tier_suggestion", "professional")
        
        # Get category and products
        category_response = supabase.table("product_categories").select("*").eq("id", str(category_id)).execute()
        if not category_response.data:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category = category_response.data[0]
        products = await marketplace_service.get_products_by_category(category_id)
        
        # Get products with pricing
        products_with_pricing = []
        for product in products:
            product_with_pricing = await marketplace_service.get_product_with_pricing(product.id, user_tier)
            if product_with_pricing:
                products_with_pricing.append(product_with_pricing)
        
        context = {
            "request": request,
            "user": user,
            "user_tier": user_tier,
            "category": category,
            "products": products_with_pricing,
            "active_tab": "marketplace"
        }
        
        return templates.TemplateResponse("category_products.html", context)
        
    except Exception as e:
        print(f"❌ Category products error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: UUID, username: str):
    """Product detail page with fair pricing"""
    try:
        # Get user data
        user_response = supabase.table("users").select("*").eq("username", username.lower()).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_response.data[0]
        user_id = UUID(user["id"])
        
        # Get user's tier
        context_response = supabase.table("context_profiles").select("tier_suggestion").eq("user_id", str(user_id)).execute()
        user_tier = "professional"
        if context_response.data:
            user_tier = context_response.data[0].get("tier_suggestion", "professional")
        
        # Get product with pricing
        product_with_pricing = await marketplace_service.get_product_with_pricing(product_id, user_tier)
        if not product_with_pricing:
            raise HTTPException(status_code=404, detail="Product not found")
        
        context = {
            "request": request,
            "user": user,
            "user_tier": user_tier,
            "product": product_with_pricing,
            "active_tab": "marketplace"
        }
        
        return templates.TemplateResponse("product_detail.html", context)
        
    except Exception as e:
        print(f"❌ Product detail error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders", response_class=HTMLResponse)
async def user_orders(request: Request, username: str):
    """User's order history"""
    try:
        # Get user data
        user_response = supabase.table("users").select("*").eq("username", username.lower()).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_response.data[0]
        user_id = UUID(user["id"])
        
        # Get user's orders
        orders = await marketplace_service.get_user_orders(user_id)
        
        context = {
            "request": request,
            "user": user,
            "orders": orders,
            "active_tab": "orders"
        }
        
        return templates.TemplateResponse("user_orders.html", context)
        
    except Exception as e:
        print(f"❌ User orders error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 