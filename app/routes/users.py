from fastapi import APIRouter, HTTPException, Request
from app.utils.supabase_client import supabase
from app.schemas import UserCreate, UserLogin
from app.utils.timezone import convert_to_eat
from app.utils.firecrawl import crawl_url
from app.utils.persona_classifier import enhance_firecrawl_persona
from app.utils.context_classifier import get_comprehensive_persona_with_context
from app.utils.tier_generator import generate_comprehensive_pricing
from app.services.packages import PackageService
from app.services.useautumn import useautumn_service
from app.utils.context_detection import context_detector
from uuid import UUID
from app.utils.security import hash_password, verify_password

router = APIRouter()

@router.post("/users")
async def create_user(user: UserCreate, request: Request):
    try:
        # Step 1: Insert user into Supabase
        payload = user.model_dump(mode="json")
        payload["password"] = hash_password(user.password)
        response = supabase.table("users").insert(payload).execute()
        user_data = response.data[0]
        user_data["created_at_eat"] = convert_to_eat(user_data.get("created_at"))

        # Step 1.5: Detect comprehensive user context from request
        context = context_detector.get_comprehensive_context(request)
        
        # Extract context information
        device_type = context['device_type']
        browser = context['browser']
        operating_system = context['os']
        language = context['language']
        location = context['location']
        timezone = context['timezone']
        country = context['country']
        region = context['region']
        city = context['city']
        coordinates = context['coordinates']
        ip_address = context['ip']
        time_of_day = context['time_of_day']
        day_of_week = context['day_of_week']
        is_weekend = context['is_weekend']
        
        # Estimate bandwidth class (this would need more sophisticated detection)
        bandwidth_class = "medium"  # default

        # Step 2: Crawl all provided social URLs and store separately
        social_data = {
            "linkedin_data": None,
            "twitter_data": None,
            "facebook_data": None,
            "github_data": None,
            "personal_website_data": None
        }
        
        summaries = []
        crawled_sources = []  # Track which sources were successfully crawled

        # Crawl LinkedIn
        if user.linkedin_url:
            result = crawl_url(str(user.linkedin_url))
            if result:
                social_data["linkedin_data"] = result
                summaries.append(result.get("firecrawl_ai_summary", ""))
                crawled_sources.append("linkedin")

        # Crawl Twitter/X
        if user.x_url:
            result = crawl_url(str(user.x_url))
            if result:
                social_data["twitter_data"] = result
                summaries.append(result.get("firecrawl_ai_summary", ""))
                crawled_sources.append("twitter")

        # Crawl GitHub
        if user.github_url:
            result = crawl_url(str(user.github_url))
            if result:
                social_data["github_data"] = result
                summaries.append(result.get("firecrawl_ai_summary", ""))
                crawled_sources.append("github")

        # Crawl Facebook
        if user.facebook_url:
            result = crawl_url(str(user.facebook_url))
            if result:
                social_data["facebook_data"] = result
                summaries.append(result.get("firecrawl_ai_summary", ""))
                crawled_sources.append("facebook")

        # Crawl Personal Website
        if user.personal_website:
            result = crawl_url(str(user.personal_website))
            if result:
                social_data["personal_website_data"] = result
                summaries.append(result.get("firecrawl_ai_summary", ""))
                crawled_sources.append("personal_website")

        # Step 3: Comprehensive persona classification (email + firecrawl + context)
        print(f"🔍 Debug - Crawled sources: {crawled_sources}")
        print(f"🔍 Debug - Email: {user.email}")
        print(f"🔍 Debug - Context: {device_type}, {browser}, {operating_system}, {language}")
        
        persona_result = get_comprehensive_persona_with_context(
            email=user.email,
            firecrawl_summaries=summaries,
            crawled_sources=crawled_sources,
            location=location,
            device_type=device_type,
            browser=browser,
            operating_system=operating_system,
            bandwidth_class=bandwidth_class,
            language=language
        )
        
        persona = persona_result["persona"]
        confidence = persona_result["confidence"]
        sources = persona_result["sources"]
        reasoning = persona_result["reasoning"]
        
        print(f"🔍 Debug - Final sources: {sources}")
        print(f"🔍 Debug - Final reasoning: {reasoning}")
        print(f"🔍 Debug - Context score: {persona_result.get('context_score', 0)}")

        # Step 3.5: Generate dynamic tier and income level
        pricing_result = generate_comprehensive_pricing(
            persona=persona,
            location=location,
            device_type=device_type,
            browser=browser,
            operating_system=operating_system,
            bandwidth_class=bandwidth_class,
            language=language,
            context_score=persona_result.get('context_score', 0),
            email=user.email  # ✅ Pass email for highest precedence
        )
        
        income_level = pricing_result["income_level"]
        tier_suggestion = pricing_result["tier_suggestion"]
        tier_details = pricing_result["tier_details"]
        pricing_reasoning = pricing_result["pricing_reasoning"]
        
        print(f"🔍 Debug - Income level: {income_level}")
        print(f"🔍 Debug - Tier suggestion: {tier_suggestion}")
        print(f"🔍 Debug - Tier details: {tier_details}")

        # Step 4: Insert context profile into Supabase
        context_payload = {
            "user_id": str(user_data["id"]),
            "username": user_data["username"],  # ✅ Add username from user data
            "location": location,               # ✅ Use detected location
            "language": language,               # ✅ Use detected language
            "device_type": device_type,         # ✅ Use detected device type
            "bandwidth_class": bandwidth_class, # ✅ Use detected bandwidth
            "browser": browser,                 # ✅ Use detected browser
            "operating_system": operating_system, # ✅ Use detected OS
            "persona_guess": persona,
            "income_level": income_level,       # ✅ Dynamic income level
            "tier_suggestion": tier_suggestion, # ✅ Dynamic tier suggestion
            # ✅ Separate social media data columns
            "linkedin_data": social_data["linkedin_data"],
            "twitter_data": social_data["twitter_data"],
            "facebook_data": social_data["facebook_data"],
            "github_data": social_data["github_data"],
            "personal_website_data": social_data["personal_website_data"]
        }
        
        # Try to add enhanced location data if columns exist
        try:
            context_payload.update({
                "country": country,
                "region": region,
                "city": city,
                "timezone": timezone,
                "coordinates": coordinates,
                "ip_address": ip_address,
                "time_of_day": time_of_day,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend
            })
            print(f"✅ Added enhanced location data: {location}, {city}, {country}")
        except Exception as e:
            print(f"⚠️ Enhanced location columns not available: {str(e)}")
            # Continue with basic location data only
        
        # Add new columns only if they exist (for backward compatibility)
        try:
            context_payload.update({
                "persona_confidence": confidence,
                "persona_sources": sources,
                "persona_reasoning": reasoning
            })
            print(f"✅ Successfully added persona data: {persona} (confidence: {confidence}, sources: {sources})")
        except Exception as e:
            # If columns don't exist, just log the persona info
            print(f"⚠️ Columns don't exist, logging persona info: {persona} (confidence: {confidence}, sources: {sources})")
            print(f"⚠️ Error: {str(e)}")

        supabase.table("context_profiles").insert(context_payload).execute()

        # Step 5: Automatically assign package based on tier
        try:
            package_service = PackageService()
            
            # Get the package that matches the user's tier
            package = package_service.get_package_by_tier_sync(tier_suggestion)
            
            # Fallback to free plan if no package found for the tier
            if not package:
                print(f"⚠️ No package found for tier: {tier_suggestion}, falling back to free plan")
                package = package_service.get_package_by_tier_sync("free")
            
            if package:
                # Create automatic subscription
                subscription_data = {
                    "user_id": str(user_data["id"]),
                    "package_id": str(package.id),
                    "status": "active",
                    "auto_renew": True,
                    "payment_method": "automatic_assignment"
                }
                
                # Insert the subscription
                supabase.table("user_packages").insert(subscription_data).execute()
                print(f"✅ Automatically assigned {package.name} package to user {user_data['username']}")
                
                # Update user data with package info
                user_data["assigned_package"] = {
                    "name": package.name,
                    "tier": package.tier,
                    "price": float(package.price),
                    "features": package.features
                }
            else:
                print(f"❌ Failed to assign any package to user {user_data['username']}")
                
        except Exception as e:
            print(f"⚠️ Error assigning package: {str(e)}")
            # Don't fail the user creation if package assignment fails

        # Step 6: Integrate with UseAutumn for dynamic pricing
        try:
            # Prepare user data for UseAutumn
            useautumn_user_data = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "location": location,
                "persona": persona,
                "tier": tier_suggestion,
                "income_level": income_level,
                "device_type": device_type,
                "browser": browser,
                "operating_system": operating_system,
                "language": language
            }
            
            # Identify user in UseAutumn system
            useautumn_result = await useautumn_service.identify_user(str(user_data["id"]), useautumn_user_data)
            
            if useautumn_result.get("success"):
                print(f"✅ User identified in UseAutumn: {user_data['username']}")
                
                # Get recommended plan from UseAutumn
                recommended_plan = useautumn_service.get_recommended_plan(useautumn_user_data)
                plan_features = useautumn_service.get_plan_features(recommended_plan)
                
                # Add UseAutumn data to user response
                user_data["useautumn"] = {
                    "identified": True,
                    "recommended_plan": recommended_plan,
                    "plan_features": plan_features,
                    "can_upgrade": recommended_plan != "free_plan"
                }
                
                print(f"🎯 UseAutumn recommended plan: {recommended_plan}")
            else:
                print(f"⚠️ UseAutumn identification failed: {useautumn_result.get('error')}")
                user_data["useautumn"] = {
                    "identified": False,
                    "error": useautumn_result.get("error")
                }
                
        except Exception as e:
            print(f"⚠️ Error integrating with UseAutumn: {str(e)}")
            user_data["useautumn"] = {
                "identified": False,
                "error": str(e)
            }
            # Don't fail the user creation if UseAutumn integration fails

        return user_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login(user: UserLogin):
    result = supabase.table("users").select("*").eq("email", user.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_data = result.data[0]
    if not verify_password(user.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "user": {
            "id": user_data["id"],
            "username": user_data["username"],
            "persona_guess": user_data.get("persona_guess", "unknown")
        }
    }