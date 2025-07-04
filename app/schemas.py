from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    linkedin_url: Optional[HttpUrl] = None
    x_url: Optional[HttpUrl] = None
    facebook_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    personal_website: Optional[HttpUrl] = None
