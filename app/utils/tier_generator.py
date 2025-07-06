from typing import Dict, Optional, List

def generate_income_level(
    persona: str,
    location: Optional[str] = None,
    device_type: Optional[str] = None,
    bandwidth_class: Optional[str] = None,
    context_score: int = 0
) -> str:
    """
    Generate income level based on persona and context data.
    """
    location_lower = location.lower() if location else ""
    
    # Student personas
    if persona == "student":
        return "low"
    
    # Tech professionals (high income)
    if persona in ["tech_professional", "entrepreneur"]:
        if "silicon valley" in location_lower or "san francisco" in location_lower:
            return "high"
        elif "seattle" in location_lower or "new york" in location_lower:
            return "high"
        else:
            return "mid_high"
    
    # Creative professionals
    if persona in ["designer", "marketing"]:
        if "new york" in location_lower or "london" in location_lower:
            return "mid_high"
        else:
            return "mid"
    
    # Finance professionals
    if persona == "finance_professional":
        if "new york" in location_lower or "london" in location_lower:
            return "high"
        else:
            return "mid_high"
    
    # Healthcare professionals
    if persona == "healthcare_professional":
        return "mid_high"
    
    # Developing regions (lower income)
    developing_regions = [
        "kenya", "uganda", "tanzania", "nigeria", "ghana", "india", "pakistan",
        "bangladesh", "philippines", "indonesia", "vietnam", "thailand"
    ]
    if any(region in location_lower for region in developing_regions):
        return "low"
    
    # Context-based adjustments
    if context_score >= 5:  # High context score suggests professional
        return "mid_high"
    elif context_score >= 3:
        return "mid"
    else:
        return "low"

def generate_tier_suggestion(
    persona: str,
    income_level: str,
    location: Optional[str] = None,
    device_type: Optional[str] = None,
    bandwidth_class: Optional[str] = None,
    email: Optional[str] = None,
    context_score: int = 0
) -> str:
    """
    Generate tier suggestion based on persona, income, and context.
    Email classification takes highest precedence.
    """
    location_lower = location.lower() if location else ""
    email_lower = email.lower() if email else ""
    
    # 🎓 EMAIL-BASED CLASSIFICATION (HIGHEST PRIORITY)
    # Student emails get student plan regardless of device/context
    if any(domain in email_lower for domain in ['.edu', '.ac.', '.school', '.college', '.university']):
        return "student"
    
    # Tech company emails get premium tier
    tech_keywords = ['tech', 'software', 'dev', 'engineering', 'startup', 'ai', 'ml', 'google', 'microsoft', 'apple', 'amazon', 'meta', 'netflix']
    if any(keyword in email_lower for keyword in tech_keywords):
        return "premium"
    
    # Finance company emails get premium tier
    finance_keywords = ['finance', 'bank', 'investment', 'wealth', 'capital', 'goldman', 'morgan', 'jpmorgan']
    if any(keyword in email_lower for keyword in finance_keywords):
        return "premium"
    
    # Healthcare company emails get standard tier
    health_keywords = ['health', 'medical', 'hospital', 'clinic', 'pharma', 'johnson', 'pfizer']
    if any(keyword in email_lower for keyword in health_keywords):
        return "standard"
    
    # 📱 CONTEXT-BASED CLASSIFICATION (LOWER PRIORITY)
    # Only applies if email classification didn't determine the tier
    
    # Student tier (heavily discounted)
    if persona == "student":
        return "student"
    
    # High-income tech professionals
    if persona in ["tech_professional", "entrepreneur"] and income_level in ["high", "mid_high"]:
        return "premium"
    
    # Finance professionals
    if persona == "finance_professional" and income_level in ["high", "mid_high"]:
        return "premium"
    
    # Low-income users or basic users get free tier
    if income_level == "low" and context_score < 3:
        return "free"
    
    # Developing regions (fair pricing)
    developing_regions = [
        "kenya", "uganda", "tanzania", "nigeria", "ghana", "india", "pakistan",
        "bangladesh", "philippines", "indonesia", "vietnam", "thailand"
    ]
    if any(region in location_lower for region in developing_regions):
        return "fair"
    
    # Mobile users (might prefer simpler pricing)
    if device_type == "mobile":
        return "standard"
    
    # Low bandwidth users (might need simpler features)
    if bandwidth_class == "low":
        return "fair"
    
    # Income-based tiers
    if income_level == "high":
        return "premium"
    elif income_level == "mid_high":
        return "standard"
    elif income_level == "mid":
        return "standard"
    elif income_level == "low":
        return "free"
    else:
        return "fair"

def get_tier_details(tier: str) -> Dict[str, any]:
    """
    Get detailed information about each tier.
    """
    tier_details = {
        "free": {
            "name": "Free Plan",
            "discount": 100,
            "features": ["Basic features", "Limited usage", "Community support"],
            "description": "Free tier for basic users"
        },
        "student": {
            "name": "Student Plan",
            "discount": 70,
            "features": ["Basic features", "Student verification required", "Limited usage"],
            "description": "Special pricing for verified students"
        },
        "fair": {
            "name": "Fair Plan",
            "discount": 50,
            "features": ["Core features", "Regional pricing", "Community support"],
            "description": "Fair pricing for developing regions"
        },
        "standard": {
            "name": "Standard Plan",
            "discount": 0,
            "features": ["All features", "Standard support", "Regular updates"],
            "description": "Standard pricing for most users"
        },
        "premium": {
            "name": "Premium Plan",
            "discount": 0,
            "features": ["All features", "Priority support", "Advanced analytics", "Custom integrations"],
            "description": "Premium pricing for professionals"
        }
    }
    
    return tier_details.get(tier, tier_details["standard"])

def generate_comprehensive_pricing(
    persona: str,
    location: Optional[str] = None,
    device_type: Optional[str] = None,
    browser: Optional[str] = None,
    operating_system: Optional[str] = None,
    bandwidth_class: Optional[str] = None,
    language: Optional[str] = None,
    context_score: int = 0,
    email: Optional[str] = None
) -> Dict[str, any]:
    """
    Generate comprehensive pricing information including income level, tier, and details.
    Email classification takes highest precedence for tier determination.
    """
    # Generate income level
    income_level = generate_income_level(
        persona=persona,
        location=location,
        device_type=device_type,
        bandwidth_class=bandwidth_class,
        context_score=context_score
    )
    
    # Generate tier suggestion (email takes highest precedence)
    tier_suggestion = generate_tier_suggestion(
        persona=persona,
        income_level=income_level,
        location=location,
        device_type=device_type,
        bandwidth_class=bandwidth_class,
        email=email,
        context_score=context_score
    )
    
    # Get tier details
    tier_details = get_tier_details(tier_suggestion)
    
    return {
        "income_level": income_level,
        "tier_suggestion": tier_suggestion,
        "tier_details": tier_details,
        "pricing_reasoning": [
            f"Persona '{persona}' typically has {income_level} income level",
            f"Location '{location}' affects pricing strategy",
            f"Device type '{device_type}' influences tier selection",
            f"Context score {context_score} indicates professional level"
        ]
    } 