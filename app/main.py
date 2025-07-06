from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.utils.supabase_client import supabase
from app.utils.timezone import convert_to_eat
from app.utils.language import language_service, detect_user_language_from_context, get_translation, get_all_translations, translate_welcome_page_content, translate_page_content
from app.routes import pricing, users, context, packages, marketplace, useautumn
from dotenv import load_dotenv
import logging
import asyncio

load_dotenv()

app = FastAPI(title="PayTosha API")

# Routers
app.include_router(pricing.router)
app.include_router(users.router)
app.include_router(context.router)
app.include_router(packages.router)
app.include_router(marketplace.router)
app.include_router(useautumn.router)

# Templates & Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

async def get_language_context(request: Request, user_language: str = None) -> dict:
    """Get language context for any page"""
    if not user_language:
        user_language = request.cookies.get("user_language", "en")
    
    # Get base translations
    translations = get_all_translations(user_language)
    
    # If user language is not English, translate the translations using Lingo.dev
    if user_language != "en":
        try:
            print(f"🌐 Translating page content to {user_language} using Lingo.dev...")
            # Translate the translations dictionary itself
            translated_translations = await translate_page_content(translations, user_language, "en")
            translations = translated_translations
        except Exception as e:
            print(f"Error translating with Lingo.dev: {e}")
            # Fallback to original translations
    
    return {
        "user_language": user_language,
        "translations": translations
    }

# Landing Page
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    language_context = await get_language_context(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        **language_context
    })

# Debug route to check database
@app.get("/debug/users")
def debug_users():
    try:
        users = supabase.table("users").select("id, username, email, created_at").execute()
        contexts = supabase.table("context_profiles").select("user_id, username, location").execute()
        
        return {
            "users": users.data,
            "contexts": contexts.data,
            "user_count": len(users.data),
            "context_count": len(contexts.data)
        }
    except Exception as e:
        return {"error": str(e)}

# Debug route to test packages dashboard
@app.get("/debug/packages/{username}")
def debug_packages(username: str):
    try:
        print(f"🔍 Debug packages - Looking for user: '{username}'")
        
        # Get user data by username (case-insensitive)
        username_lower = username.lower()
        user_response = supabase.table("users").select("*").eq("username", username_lower).execute()
        
        if not user_response.data:
            user_response = supabase.table("users").select("*").eq("username", username).execute()
            
        if not user_response.data:
            user_response = supabase.table("users").select("*").ilike("username", f"%{username}%").execute()
            
        if not user_response.data:
            return {"error": f"User '{username}' not found"}
            
        user = user_response.data[0]
        user_id = user["id"]
        
        # Check if user_id is a valid UUID
        try:
            from uuid import UUID
            UUID(user_id)
        except ValueError:
            return {"error": f"Invalid user ID format: {user_id}"}
        
        # Get user packages
        packages_response = supabase.table("user_packages").select("*").eq("user_id", user_id).execute()
        
        return {
            "user": user,
            "user_id": user_id,
            "user_packages": packages_response.data,
            "packages_count": len(packages_response.data)
        }
        
    except Exception as e:
        return {"error": str(e)}

# Registration Page
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    language_context = await get_language_context(request)
    return templates.TemplateResponse("register.html", {
        "request": request,
        **language_context
    })

# Login Page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    language_context = await get_language_context(request)
    return templates.TemplateResponse("login.html", {
        "request": request,
        **language_context
    })

# Pricing Page
@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    language_context = await get_language_context(request)
    return templates.TemplateResponse("pricing.html", {
        "request": request,
        **language_context
    })

# Language selection endpoint
@app.post("/set-language")
async def set_language(request: Request):
    """Set user's preferred language"""
    try:
        data = await request.json()
        language = data.get("language", "en")
        
        # Store in cookie
        from fastapi.responses import JSONResponse
        response = JSONResponse({"success": True, "language": language})
        response.set_cookie(key="user_language", value=language, max_age=365*24*60*60)  # 1 year
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

# Text translation endpoint using Lingo.dev
@app.post("/translate-text")
async def translate_text_endpoint(request: Request):
    """Translate text using Lingo.dev API"""
    try:
        data = await request.json()
        text = data.get("text", "")
        target_language = data.get("target_language", "en")
        source_language = data.get("source_language", "en")
        
        if not text or target_language == source_language:
            return {"translated_text": text}
        
        # Use Lingo.dev API to translate
        translated_text = await language_service.translate_text(text, target_language, source_language)
        
        return {"translated_text": translated_text}
    except Exception as e:
        print(f"Translation endpoint error: {e}")
        return {"translated_text": text, "error": str(e)}

# API route to get user context
@app.get("/api/user-context/{username}")
async def get_user_context(username: str):
    """Get user context profile for pricing page"""
    try:
        # Get context profile
        context_response = supabase.table("context_profiles").select("*").eq("username", username.lower()).execute()
        
        if not context_response.data:
            context_response = supabase.table("context_profiles").select("*").eq("username", username).execute()
            
        if not context_response.data:
            return {"error": "User context not found"}
            
        context_data = context_response.data[0]
        
        return {
            "location": context_data.get("location"),
            "persona": context_data.get("persona_guess"),
            "income_level": context_data.get("income_level"),
            "device_type": context_data.get("device_type"),
            "language": context_data.get("language"),
            "tier": context_data.get("tier_suggestion")
        }
    except Exception as e:
        return {"error": str(e)}

# API route to get user data
@app.get("/api/user/{username}")
async def get_user_data(username: str):
    """Get user data for pricing page"""
    try:
        # Get user data
        user_response = supabase.table("users").select("id, username, email").eq("username", username.lower()).execute()
        
        if not user_response.data:
            user_response = supabase.table("users").select("id, username, email").eq("username", username).execute()
            
        if not user_response.data:
            return {"error": "User not found"}
            
        user_data = user_response.data[0]
        
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"]
        }
    except Exception as e:
        return {"error": str(e)}

# Test UseAutumn endpoint
@app.get("/test-useautumn")
async def test_useautumn():
    """Test if UseAutumn service is working"""
    try:
        from app.services.useautumn import useautumn_service
        return {
            "status": "success",
            "message": "UseAutumn service is working",
            "products": list(useautumn_service.products.keys()),
            "api_key_configured": bool(useautumn_service.api_key)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"UseAutumn service error: {str(e)}"
        }

# Mock checkout endpoint for testing
@app.get("/mock-checkout")
async def mock_checkout(product: str, user: str):
    """Mock checkout page for testing upgrades"""
    return {
        "message": "Mock Checkout Page",
        "product": product,
        "user": user,
        "status": "success",
        "note": "This is a mock checkout. In production, this would redirect to Stripe."
    }

# Welcome Page
@app.get("/welcome", response_class=HTMLResponse)
async def welcome_page(request: Request, username: str):
    try:
        # Debug logging
        print(f"🔍 Looking for user: '{username}'")
        
        # Convert username to lowercase for case-insensitive lookup
        username_lower = username.lower()
        print(f"🔍 Lowercase username: '{username_lower}'")
        
        # First try exact match
        user_res = supabase.table("users").select("*").eq("username", username_lower).execute()
        print(f"🔍 Exact match result: {len(user_res.data) if user_res.data else 0} users found")
        
        if not user_res.data:
            # Try original case
            user_res = supabase.table("users").select("*").eq("username", username).execute()
            print(f"🔍 Original case result: {len(user_res.data) if user_res.data else 0} users found")
            
            if not user_res.data:
                # Try case-insensitive search as fallback
                user_res = supabase.table("users").select("*").ilike("username", f"%{username}%").execute()
                print(f"🔍 ILIKE result: {len(user_res.data) if user_res.data else 0} users found")
                
                if not user_res.data:
                    # List all users for debugging
                    all_users = supabase.table("users").select("username").execute()
                    print(f"🔍 All users in database: {[u['username'] for u in all_users.data]}")
                    raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        user = user_res.data[0]
        print(f"✅ Found user: {user['username']}")

        # Look for context profile
        context_res = supabase.table("context_profiles").select("*").eq("username", username_lower).execute()
        print(f"🔍 Context exact match: {len(context_res.data) if context_res.data else 0} profiles found")
        
        if not context_res.data:
            context_res = supabase.table("context_profiles").select("*").eq("username", username).execute()
            print(f"🔍 Context original case: {len(context_res.data) if context_res.data else 0} profiles found")
            
            if not context_res.data:
                context_res = supabase.table("context_profiles").select("*").ilike("username", f"%{username}%").execute()
                print(f"🔍 Context ILIKE: {len(context_res.data) if context_res.data else 0} profiles found")
        
        context = context_res.data[0] if context_res.data else {}
        print(f"✅ Context profile: {context.get('username', 'Not found')}")

        # Get user's assigned package
        package_res = supabase.table("user_packages").select("*, packages(*)").eq("user_id", user["id"]).eq("status", "active").execute()
        assigned_package = None
        if package_res.data:
            package_data = package_res.data[0]
            assigned_package = {
                "name": package_data["packages"]["name"],
                "tier": package_data["packages"]["tier"],
                "price": package_data["packages"]["price"],
                "features": package_data["packages"]["features"]
            }

        user["created_at_eat"] = convert_to_eat(user.get("created_at"))
        if assigned_package:
            user["assigned_package"] = assigned_package

        # Detect user's preferred language
        # First check for cookie preference
        user_language = request.cookies.get("user_language")
        if not user_language:
            # Fall back to context-based detection
            user_language = detect_user_language_from_context(context)
        
        # Translate dynamic content using Lingo.dev
        translated_data = await translate_welcome_page_content(user, context, user_language)
        translated_user = translated_data["user"]
        translated_context = translated_data["context"]
        
        # Get comprehensive translations
        translations = {
            "welcome": get_translation("welcome", user_language),
            "dashboard": get_translation("dashboard", user_language),
            "marketplace": get_translation("marketplace", user_language),
            "packages": get_translation("packages", user_language),
            "profile": get_translation("profile", user_language),
            "settings": get_translation("settings", user_language),
            "logout": get_translation("logout", user_language),
            "fair_pricing": get_translation("fair_pricing", user_language),
            "student_discount": get_translation("student_discount", user_language),
            "premium_features": get_translation("premium_features", user_language),
            # Welcome page specific translations
            "account_info": get_translation("account_info", user_language),
            "full_name": get_translation("full_name", user_language),
            "username": get_translation("username", user_language),
            "email": get_translation("email", user_language),
            "account_created": get_translation("account_created", user_language),
            "location_context": get_translation("location_context", user_language),
            "location": get_translation("location", user_language),
            "country": get_translation("country", user_language),
            "city": get_translation("city", user_language),
            "timezone": get_translation("timezone", user_language),
            "time_of_day": get_translation("time_of_day", user_language),
            "coordinates": get_translation("coordinates", user_language),
            "mobile_optimized": get_translation("mobile_optimized", user_language),
            "desktop_experience": get_translation("desktop_experience", user_language),
            "using_browser": get_translation("using_browser", user_language),
            "on_os": get_translation("on_os", user_language),
            "smart_insights": get_translation("smart_insights", user_language),
            "persona_guess": get_translation("persona_guess", user_language),
            "confidence": get_translation("confidence", user_language),
            "sources": get_translation("sources", user_language),
            "reasoning": get_translation("reasoning", user_language),
            "student_resources": get_translation("student_resources", user_language),
            "student_verification_required": get_translation("student_verification_required", user_language),
            "access_educational_tools": get_translation("access_educational_tools", user_language),
            "limited_usage_student": get_translation("limited_usage_student", user_language),
            "developer_tools": get_translation("developer_tools", user_language),
            "advanced_analytics": get_translation("advanced_analytics", user_language),
            "api_access": get_translation("api_access", user_language),
            "priority_support": get_translation("priority_support", user_language),
            "freelancer_tools": get_translation("freelancer_tools", user_language),
            "project_management": get_translation("project_management", user_language),
            "client_billing": get_translation("client_billing", user_language),
            "portfolio_showcase": get_translation("portfolio_showcase", user_language),
            "entrepreneur_features": get_translation("entrepreneur_features", user_language),
            "business_analytics": get_translation("business_analytics", user_language),
            "team_management": get_translation("team_management", user_language),
            "growth_tracking": get_translation("growth_tracking", user_language),
            "dynamic_pricing": get_translation("dynamic_pricing", user_language),
            "income_level": get_translation("income_level", user_language),
            "suggested_tier": get_translation("suggested_tier", user_language),
            "package_assigned": get_translation("package_assigned", user_language),
            "package_assigned_desc": get_translation("package_assigned_desc", user_language),
            "manage_package": get_translation("manage_package", user_language),
            "premium_plan_title": get_translation("premium_plan_title", user_language),
            "premium_plan_desc": get_translation("premium_plan_desc", user_language),
            "student_plan_title": get_translation("student_plan_title", user_language),
            "student_plan_desc": get_translation("student_plan_desc", user_language),
            "fair_plan_title": get_translation("fair_plan_title", user_language),
            "fair_plan_desc": get_translation("fair_plan_desc", user_language),
            "free_plan_title": get_translation("free_plan_title", user_language),
            "free_plan_desc": get_translation("free_plan_desc", user_language),
            "standard_plan_title": get_translation("standard_plan_title", user_language),
            "standard_plan_desc": get_translation("standard_plan_desc", user_language),
            "low_bandwidth_mode": get_translation("low_bandwidth_mode", user_language),
            "low_bandwidth_desc": get_translation("low_bandwidth_desc", user_language),
            "high_performance_mode": get_translation("high_performance_mode", user_language),
            "high_performance_desc": get_translation("high_performance_desc", user_language),
            "social_summary": get_translation("social_summary", user_language),
            "no_social_data": get_translation("no_social_data", user_language),
            "browse_marketplace": get_translation("browse_marketplace", user_language),
            "discover_products": get_translation("discover_products", user_language),
            "upgrade_premium": get_translation("upgrade_premium", user_language),
            "unlock_features": get_translation("unlock_features", user_language),
            "complete_verification": get_translation("complete_verification", user_language),
            "verify_student": get_translation("verify_student", user_language),
            "access_premium_dashboard": get_translation("access_premium_dashboard", user_language),
            "explore_features": get_translation("explore_features", user_language),
            "go_to_dashboard": get_translation("go_to_dashboard", user_language),
            "start_exploring": get_translation("start_exploring", user_language),
            "mobile_optimized_exp": get_translation("mobile_optimized_exp", user_language),
            "desktop_full_exp": get_translation("desktop_full_exp", user_language),
            "detecting": get_translation("detecting", user_language),
            "unknown": get_translation("unknown", user_language),
            "no_summary": get_translation("no_summary", user_language),
            "source": get_translation("source", user_language)
        }

        return templates.TemplateResponse("welcome.html", {
            "request": request,
            "user": translated_user,
            "context": translated_context,
            "persona": translated_context.get("persona_guess"),
            "tier": translated_context.get("tier_suggestion"),
            "device_type": translated_context.get("device_type"),
            "bandwidth": translated_context.get("bandwidth_class"),
            "income_level": translated_context.get("income_level"),
            "browser": translated_context.get("browser"),
            "operating_system": translated_context.get("operating_system"),
            "user_language": user_language,
            "translations": translations
        })

    except Exception as e:
        logging.exception("Welcome page error")
        # Return a fallback template with minimal data instead of raising an error
        return templates.TemplateResponse("welcome.html", {
            "request": request,
            "user": {"username": username, "first_name": "User", "last_name": "Unknown", "email": "unknown@example.com", "created_at_eat": "Unknown"},
            "context": {"location": "Unknown", "persona_guess": "unknown", "tier_suggestion": "free", "device_type": "desktop", "bandwidth_class": "medium", "income_level": "unknown", "browser": "unknown", "operating_system": "unknown"},
            "persona": "unknown",
            "tier": "free",
            "device_type": "desktop",
            "bandwidth": "medium",
            "income_level": "unknown",
            "browser": "unknown",
            "operating_system": "unknown"
        })

# Adaptive Dashboard Routing
@app.get("/dashboard", response_class=HTMLResponse)
async def adaptive_dashboard(request: Request, username: str):
    """
    Adaptive dashboard that redirects users based on their persona and tier.
    """
    try:
        # Get user context
        context_res = supabase.table("context_profiles").select("*").eq("username", username).execute()
        if not context_res.data:
            raise HTTPException(status_code=404, detail="User context not found")
        
        context = context_res.data[0]
        persona = context.get("persona_guess")
        tier = context.get("tier_suggestion")
        
        # Create a user object for templates
        user = {"username": username}
        
        # Get language context
        language_context = await get_language_context(request)
        
        # Redirect based on persona and tier
        if persona == "student" and tier == "student":
            return templates.TemplateResponse("student_dashboard.html", {
                "request": request,
                "username": username,
                "context": context,
                "user": user,
                **language_context
            })
        elif persona == "tech_professional" and tier == "premium":
            return templates.TemplateResponse("premium_dashboard.html", {
                "request": request,
                "username": username,
                "context": context,
                "user": user,
                **language_context
            })
        elif persona == "freelancer":
            return templates.TemplateResponse("freelancer_dashboard.html", {
                "request": request,
                "username": username,
                "context": context,
                "user": user,
                **language_context
            })
        else:
            # Default dashboard
            return templates.TemplateResponse("default_dashboard.html", {
                "request": request,
                "username": username,
                "context": context,
                "user": user,
                **language_context
            })
            
    except Exception as e:
        logging.exception("Dashboard routing error")
        raise HTTPException(status_code=500, detail="Something went wrong.")
