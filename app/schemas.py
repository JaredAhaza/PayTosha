from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import re

# 🔹 User creation input with multiple optional social links
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    linkedin_url: Optional[HttpUrl] = None
    x_url: Optional[HttpUrl] = None
    facebook_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    personal_website: Optional[HttpUrl] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for at least one digit
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        
        # Only allow alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        
        return v.lower()  # Convert to lowercase for consistency


# 🔹 Context Profile creation payload for Supabase
class ContextProfileCreate(BaseModel):
    user_id: UUID  # FK from users.id
    username: str
    location: Optional[str] = None
    language: Optional[str] = None
    device_type: Optional[str] = None
    bandwidth_class: Optional[str] = None
    browser: Optional[str] = None
    operating_system: Optional[str] = None
    persona_guess: Optional[str] = None
    income_level: Optional[str] = None
    tier_suggestion: Optional[str] = None
    # Social media data - separate columns for each platform
    linkedin_data: Optional[Dict] = None
    twitter_data: Optional[Dict] = None
    facebook_data: Optional[Dict] = None
    github_data: Optional[Dict] = None
    personal_website_data: Optional[Dict] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 🔹 Package schemas
class PackageBase(BaseModel):
    name: str
    tier: str
    price: Decimal
    original_price: Decimal
    discount_percentage: int = 0
    features: List[str]
    description: Optional[str] = None
    max_users: int = 1
    storage_limit_gb: int = 1
    api_calls_per_month: int = 1000
    support_level: str = "community"

class PackageCreate(PackageBase):
    pass

class PackageUpdate(BaseModel):
    name: Optional[str] = None
    tier: Optional[str] = None
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    discount_percentage: Optional[int] = None
    features: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    max_users: Optional[int] = None
    storage_limit_gb: Optional[int] = None
    api_calls_per_month: Optional[int] = None
    support_level: Optional[str] = None

class Package(PackageBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 🔹 User Package (Subscription) schemas
class UserPackageBase(BaseModel):
    user_id: UUID
    package_id: UUID
    status: str = "active"
    auto_renew: bool = True
    payment_method: Optional[str] = None

class UserPackageCreate(UserPackageBase):
    pass

class UserPackageUpdate(BaseModel):
    status: Optional[str] = None
    auto_renew: Optional[bool] = None
    payment_method: Optional[str] = None
    end_date: Optional[datetime] = None

class UserPackage(UserPackageBase):
    id: UUID
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    package: Optional[Package] = None  # Include the related package data

    class Config:
        from_attributes = True

# 🔹 Package with subscription details
class PackageWithSubscription(Package):
    user_subscription: Optional[UserPackage] = None
    is_subscribed: bool = False
    can_upgrade: bool = False
    can_downgrade: bool = False

# 🔹 Package comparison
class PackageComparison(BaseModel):
    current_package: Optional[PackageWithSubscription] = None
    available_packages: List[Package]
    recommended_package: Optional[Package] = None
    upgrade_path: List[Package] = []
    downgrade_path: List[Package] = []

# 🔹 Marketplace schemas
class ProductCategory(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    icon: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Product(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category: Optional[str]
    category_id: Optional[UUID]
    base_price: Decimal
    currency: str
    image_url: Optional[str]
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TierPricing(BaseModel):
    id: UUID
    product_id: UUID
    tier: str
    price_multiplier: Decimal
    fixed_price: Optional[Decimal]
    reasoning: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductWithPricing(BaseModel):
    product: Product
    tier_pricing: List[TierPricing]
    user_tier: Optional[str] = None
    user_price: Optional[Decimal] = None
    fairness_reasoning: Optional[str] = None

    class Config:
        from_attributes = True

class Order(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    tier: str
    original_price: Decimal
    final_price: Decimal
    currency: str
    status: str
    payment_method: Optional[str]
    fairness_reasoning: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[UUID] = None
    base_price: Decimal
    currency: str = "USD"
    image_url: Optional[str] = None

class TierPricingCreate(BaseModel):
    tier: str
    price_multiplier: Decimal = Decimal("1.00")
    fixed_price: Optional[Decimal] = None
    reasoning: Optional[str] = None

class OrderCreate(BaseModel):
    product_id: UUID
    payment_method: str = "stripe"
