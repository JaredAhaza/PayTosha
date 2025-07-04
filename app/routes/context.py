from fastapi import APIRouter, HTTPException
from app.utils.supabase_client import supabase
from app.schemas import ContextProfileCreate

router = APIRouter()

@router.post("/context")
def create_context_profile(context: ContextProfileCreate):
    try:
        payload = context.model_dump(mode="json")

        # Ensure user_id is present
        if not payload.get("user_id"):
            raise HTTPException(status_code=422, detail="Missing user_id for context profile")

        response = supabase.table("context_profiles").insert(payload).execute()

        if response.data:
            return {"message": "Context profile created", "data": response.data}
        else:
            return {"message": "Insert attempted but no data returned", "error": str(response)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
