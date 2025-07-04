from fastapi import APIRouter, HTTPException
from app.utils.supabase_client import supabase
from app.schemas import UserCreate

router = APIRouter()

@router.post("/users")
def create_user(user: UserCreate):
    try:
        payload = user.model_dump(mode="json")  # ensures HttpUrl becomes a string
        response = supabase.table("users").insert(payload).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

