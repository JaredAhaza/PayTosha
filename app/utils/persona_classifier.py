import re
from typing import List, Dict, Optional

def classify_persona_from_email(email: str) -> Optional[str]:
    """
    Classify user persona based on email domain and patterns.
    """
    email_lower = email.lower()
    
    # Student emails - highest priority
    if any(domain in email_lower for domain in ['.edu', '.ac.', '.school', '.college', '.university']):
        return "student"
    
    # Extract domain for further analysis
    domain = email_lower.split('@')[1] if '@' in email_lower else ''
    
    # Check for tech company patterns
    tech_keywords = ['tech', 'software', 'dev', 'engineering', 'startup', 'ai', 'ml', 'google', 'microsoft', 'apple', 'amazon', 'meta', 'netflix']
    if any(keyword in domain for keyword in tech_keywords):
        return "tech_professional"
    
    # Check for finance patterns
    finance_keywords = ['finance', 'bank', 'investment', 'wealth', 'capital', 'goldman', 'morgan', 'jpmorgan']
    if any(keyword in domain for keyword in finance_keywords):
        return "finance_professional"
    
    # Check for healthcare patterns
    health_keywords = ['health', 'medical', 'hospital', 'clinic', 'pharma', 'johnson', 'pfizer']
    if any(keyword in domain for keyword in health_keywords):
        return "healthcare_professional"
    
    return None

def classify_persona_from_social_data(social_data: List[Dict]) -> Optional[str]:
    """
    Enhanced persona classification from social media data.
    """
    if not social_data:
        return None
    
    # Combine all summaries for analysis
    all_summaries = " ".join([
        item.get("firecrawl_ai_summary", "").lower() 
        for item in social_data 
        if item.get("success", True)
    ])
    
    # Define persona keywords with weights
    persona_keywords = {
        "student": ["student", "university", "college", "academic", "study", "research", "thesis", "campus"],
        "freelancer": ["freelancer", "freelance", "independent", "contractor", "self-employed", "consultant"],
        "entrepreneur": ["entrepreneur", "founder", "startup", "ceo", "co-founder", "business owner", "startup founder"],
        "tech_professional": ["software engineer", "developer", "programmer", "tech", "coding", "software", "engineer", "developer"],
        "designer": ["designer", "ui/ux", "graphic designer", "creative", "art director", "visual"],
        "marketing": ["marketing", "digital marketing", "social media", "brand", "advertising", "pr"],
        "finance": ["finance", "banking", "investment", "accounting", "financial", "analyst"],
        "healthcare": ["doctor", "nurse", "medical", "healthcare", "physician", "health"],
        "education": ["teacher", "professor", "educator", "academic", "lecturer", "instructor"],
        "consultant": ["consultant", "advisor", "strategist", "expert", "specialist"]
    }
    
    # Score each persona
    persona_scores = {}
    for persona, keywords in persona_keywords.items():
        score = sum(1 for keyword in keywords if keyword in all_summaries)
        if score > 0:
            persona_scores[persona] = score
    
    # Return the highest scoring persona
    if persona_scores:
        return max(persona_scores, key=persona_scores.get)
    
    return None

def classify_persona_from_linkedin_data(linkedin_data: List[Dict]) -> Optional[str]:
    """
    Specialized classification for LinkedIn data.
    """
    if not linkedin_data:
        return None
    
    # Look for LinkedIn-specific data
    for item in linkedin_data:
        if not item.get("success", True):
            continue
            
        summary = item.get("firecrawl_ai_summary", "").lower()
        
        # LinkedIn often has job titles and company info
        if "linkedin" in item.get("url", "").lower():
            # Check for job titles
            job_titles = {
                "student": ["student", "intern", "graduate student"],
                "entrepreneur": ["founder", "ceo", "co-founder", "entrepreneur", "startup"],
                "tech_professional": ["software engineer", "developer", "programmer", "tech lead", "engineering"],
                "designer": ["designer", "ui/ux", "creative director", "art director"],
                "marketing": ["marketing", "brand", "digital marketing", "growth"],
                "finance": ["finance", "investment", "banking", "financial analyst"],
                "consultant": ["consultant", "advisor", "strategist"]
            }
            
            for persona, titles in job_titles.items():
                if any(title in summary for title in titles):
                    return persona
    
    return None

def get_comprehensive_persona(email: str, social_data: List[Dict], linkedin_data: List[Dict] = None) -> str:
    """
    Comprehensive persona classification combining email, social data, and LinkedIn data.
    Returns the most confident classification.
    """
    # Priority order: LinkedIn > Email > Social Data > Default
    
    # 1. Try LinkedIn classification first (most reliable)
    if linkedin_data:
        linkedin_persona = classify_persona_from_linkedin_data(linkedin_data)
        if linkedin_persona:
            return linkedin_persona
    
    # 2. Try email classification
    email_persona = classify_persona_from_email(email)
    if email_persona:
        return email_persona
    
    # 3. Try social data classification
    social_persona = classify_persona_from_social_data(social_data)
    if social_persona:
        return social_persona
    
    # 4. Default fallback
    return "general"

def get_persona_confidence_score(email: str, social_data: List[Dict], linkedin_data: List[Dict] = None) -> Dict[str, any]:
    """
    Get persona classification with confidence score and reasoning.
    """
    result = {
        "persona": "general",
        "confidence": "low",
        "sources": [],
        "reasoning": []
    }
    
    # Check LinkedIn
    if linkedin_data:
        linkedin_persona = classify_persona_from_linkedin_data(linkedin_data)
        if linkedin_persona:
            result["persona"] = linkedin_persona
            result["confidence"] = "high"
            result["sources"].append("linkedin")
            result["reasoning"].append(f"LinkedIn profile analysis indicated {linkedin_persona}")
    
    # Check email
    email_persona = classify_persona_from_email(email)
    if email_persona and result["confidence"] != "high":
        result["persona"] = email_persona
        result["confidence"] = "medium"
        result["sources"].append("email")
        result["reasoning"].append(f"Email domain analysis indicated {email_persona}")
    
    # Check social data
    social_persona = classify_persona_from_social_data(social_data)
    if social_persona and result["confidence"] == "low":
        result["persona"] = social_persona
        result["confidence"] = "medium"
        result["sources"].append("social_media")
        result["reasoning"].append(f"Social media analysis indicated {social_persona}")
    
    return result

def enhance_firecrawl_persona(email: str, firecrawl_summaries: List[str], crawled_sources: List[str] = None) -> Dict[str, any]:
    """
    Enhance the existing firecrawl persona classification with email analysis.
    This works with your existing firecrawl system.
    """
    # First, try email classification
    email_persona = classify_persona_from_email(email)
    
    # Then use your existing firecrawl logic
    full_summary = " ".join(firecrawl_summaries).lower()
    
    # Your existing firecrawl persona logic
    if "freelancer" in full_summary:
        firecrawl_persona = "freelancer"
    elif "student" in full_summary:
        firecrawl_persona = "student"
    elif "engineer" in full_summary:
        firecrawl_persona = "engineer"
    elif "developer" in full_summary:
        firecrawl_persona = "developer"
    else:
        firecrawl_persona = "general"
    
    # Priority: Email classification overrides firecrawl if email is more specific
    if email_persona == "student":
        final_persona = "student"
        confidence = "high"
        sources = ["email"]
        reasoning = [f"Email domain ({email}) indicates student status"]
    elif email_persona and firecrawl_persona == "general":
        final_persona = email_persona
        confidence = "medium"
        sources = ["email"]
        reasoning = [f"Email domain analysis indicated {email_persona}"]
    else:
        final_persona = firecrawl_persona
        confidence = "medium"
        # Use actual crawled sources instead of generic "firecrawl"
        sources = crawled_sources if crawled_sources else ["firecrawl"]
        reasoning = [f"Social media analysis from {', '.join(sources)} indicated {firecrawl_persona}"]
        if email_persona:
            sources.append("email")
            reasoning.append(f"Email domain also suggested {email_persona}")
    
    return {
        "persona": final_persona,
        "confidence": confidence,
        "sources": sources,
        "reasoning": reasoning,
        "email_persona": email_persona,
        "firecrawl_persona": firecrawl_persona
    } 