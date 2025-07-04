from fastapi import APIRouter, HTTPException
from app.utils.supabase_client import supabase
from app.schemas import UserCreate
from app.utils.timezone import convert_to_eat  # ✅ added import

router = APIRouter()

@router.post("/users")
def create_user(user: UserCreate):
    try:
        payload = user.model_dump(mode="json")
        response = supabase.table("users").insert(payload).execute()
        user_data = response.data[0]  # get the inserted user

        # ✅ Add EAT timestamp
        user_data["created_at_eat"] = convert_to_eat(user_data.get("created_at"))

        return user_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
