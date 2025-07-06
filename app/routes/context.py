from fastapi import APIRouter, HTTPException, Request
from app.utils.supabase_client import supabase
from app.schemas import ContextProfileCreate
from app.utils.context_classifier import classify_persona_from_context
from app.utils.context_detection import context_detector
from app.utils.geolocation import geolocation_service
import json

router = APIRouter()

@router.post("/context")
def create_context_profile(context: ContextProfileCreate):
    try:
        payload = context.model_dump(mode="json")

        # ✅ Ensure username is present instead of user_id
        if not payload.get("username"):
            raise HTTPException(status_code=422, detail="Missing username for context profile")

        response = supabase.table("context_profiles").insert(payload).execute()

        if response.data:
            return {"message": "Context profile created", "data": response.data}
        else:
            return {"message": "Insert attempted but no data returned", "error": str(response)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-context")
def detect_user_context(request: Request):
    """
    Detect user context from request headers and user agent.
    This endpoint can be called from the frontend to get context data.
    """
    try:
        # Get user agent string
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Get client IP for location detection (basic)
        client_ip = request.client.host if request.client else "unknown"
        
        # Parse user agent for device and browser info
        device_type = "desktop"  # default
        browser = "unknown"
        operating_system = "unknown"
        
        # Detect operating system
        if "windows" in user_agent:
            operating_system = "Windows"
        elif "mac" in user_agent:
            operating_system = "macOS"
        elif "linux" in user_agent:
            operating_system = "Linux"
        elif "android" in user_agent:
            operating_system = "Android"
            device_type = "mobile"
        elif "iphone" in user_agent or "ipad" in user_agent:
            operating_system = "iOS"
            device_type = "mobile" if "iphone" in user_agent else "tablet"
        
        # Detect browser
        if "chrome" in user_agent:
            browser = "Chrome"
        elif "firefox" in user_agent:
            browser = "Firefox"
        elif "safari" in user_agent:
            browser = "Safari"
        elif "edge" in user_agent:
            browser = "Edge"
        elif "opera" in user_agent:
            browser = "Opera"
        
        # Detect device type
        if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
            device_type = "mobile"
        elif "tablet" in user_agent or "ipad" in user_agent:
            device_type = "tablet"
        elif "desktop" in user_agent or "windows" in user_agent or "mac" in user_agent or "linux" in user_agent:
            device_type = "desktop"
        
        # Estimate bandwidth class (this would need more sophisticated detection)
        bandwidth_class = "medium"  # default
        
        # Get language from headers
        language = request.headers.get("accept-language", "en").split(",")[0].split("-")[0]
        
        # Basic location detection (you might want to use a geolocation service)
        location = "unknown"
        
        # Classify persona from context
        context_result = classify_persona_from_context(
            location=location,
            device_type=device_type,
            browser=browser,
            operating_system=operating_system,
            bandwidth_class=bandwidth_class,
            language=language
        )
        
        return {
            "context_data": {
                "location": location,
                "device_type": device_type,
                "browser": browser,
                "operating_system": operating_system,
                "bandwidth_class": bandwidth_class,
                "language": language,
                "client_ip": client_ip
            },
            "persona_analysis": context_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-location")
def test_location(request: Request):
    """
    Test endpoint to verify location detection functionality
    """
    try:
        # Get comprehensive context
        context = context_detector.get_comprehensive_context(request)
        
        # Get client IP
        client_ip = geolocation_service.get_client_ip(request)
        
        # Test IP-based location detection
        location_data = geolocation_service.get_location_from_ip(client_ip)
        
        return {
            "success": True,
            "client_ip": client_ip,
            "location_display": context['location'],
            "location_data": location_data,
            "context_summary": context_detector.get_context_summary(context),
            "full_context": context
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "client_ip": geolocation_service.get_client_ip(request) if 'geolocation_service' in locals() else "Unknown"
        }

@router.get("/location-info")
def get_location_info(request: Request):
    """
    Get detailed location information for the current request
    """
    try:
        context = context_detector.get_comprehensive_context(request)
        
        return {
            "location": context['location'],
            "country": context['country'],
            "region": context['region'],
            "city": context['city'],
            "timezone": context['timezone'],
            "coordinates": context['coordinates'],
            "ip": context['ip'],
            "time_of_day": context['time_of_day'],
            "day_of_week": context['day_of_week'],
            "is_weekend": context['is_weekend']
        }
    except Exception as e:
        return {
            "error": str(e),
            "location": "Unknown"
        }
