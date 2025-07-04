from fastapi import APIRouter
from app.services.persona import classify_user

router = APIRouter()

@router.post("/pricing")
async def get_pricing(user_data: dict):
    persona = classify_user(user_data)
    return {"tier": persona["tier"], "details": persona}
