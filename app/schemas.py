from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict
from uuid import UUID

# 🔹 User creation input with multiple optional social links
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    linkedin_url: Optional[HttpUrl] = None
    x_url: Optional[HttpUrl] = None  # Twitter/X
    facebook_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    personal_website: Optional[HttpUrl] = None

# 🔹 Context Profile creation payload for Supabase
class ContextProfileCreate(BaseModel):
    user_id: UUID  # FK from users.id
    location: Optional[str] = None
    language: Optional[str] = None
    device_type: Optional[str] = None
    bandwidth_class: Optional[str] = None
    persona_guess: Optional[str] = None
    income_level: Optional[str] = None
    social_data: Optional[Dict] = None  # 🔁 renamed from linkedin_data
    tier_suggestion: Optional[str] = None
