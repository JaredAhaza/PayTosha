from fastapi import APIRouter, HTTPException
from app.utils.supabase_client import supabase
from app.schemas import UserCreate
from app.utils.timezone import convert_to_eat
from app.utils.firecrawl import crawl_url
from uuid import UUID

router = APIRouter()

@router.post("/users")
def create_user(user: UserCreate):
    try:
        # Step 1: Insert user into Supabase
        payload = user.model_dump(mode="json")
        response = supabase.table("users").insert(payload).execute()
        user_data = response.data[0]
        user_data["created_at_eat"] = convert_to_eat(user_data.get("created_at"))

        # Step 2: Crawl all provided social URLs
        social_urls = [
            user.linkedin_url,
            user.x_url,
            user.github_url,
            user.facebook_url,
            user.personal_website
        ]

        crawled_data = []
        summaries = []

        for url in social_urls:
            if url:
                result = crawl_url(str(url))
                if result:
                    crawled_data.append(result)
                    summaries.append(result.get("firecrawl_ai_summary", ""))

        # Step 3: Infer persona from AI summaries
        full_summary = " ".join(summaries).lower()
        if "freelancer" in full_summary:
            persona = "freelancer"
        elif "student" in full_summary:
            persona = "student"
        elif "engineer" in full_summary:
            persona = "engineer"
        elif "developer" in full_summary:
            persona = "developer"
        else:
            persona = "general"

        # Step 4: Insert context profile into Supabase
        context_payload = {
            "user_id": str(user_data["id"]),
            "location": "unknown",              # optionally infer later
            "language": "en",
            "device_type": "unknown",
            "bandwidth_class": "medium",
            "persona_guess": persona,
            "income_level": "mid",
            "tier_suggestion": "fair",          # optionally infer later
            "linkedin_data": crawled_data or None  # this must match Supabase schema
        }

        supabase.table("context_profiles").insert(context_payload).execute()

        return user_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
