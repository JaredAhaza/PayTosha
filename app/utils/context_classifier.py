from typing import Dict, Optional, List

def classify_persona_from_context(
    location: Optional[str] = None,
    device_type: Optional[str] = None,
    browser: Optional[str] = None,
    operating_system: Optional[str] = None,
    bandwidth_class: Optional[str] = None,
    language: Optional[str] = None
) -> Dict[str, any]:
    """
    Classify user persona based on context data (location, device, browser, OS, bandwidth).
    """
    context_score = 0
    context_reasons = []
    context_sources = []
    
    # Location-based classification
    if location:
        context_sources.append("location")
        location_lower = location.lower()
        
        # Student locations (universities, colleges)
        student_locations = [
            "cambridge", "oxford", "stanford", "mit", "harvard", "berkeley", "ucla", "nyu",
            "college", "university", "campus", "student", "academic"
        ]
        if any(term in location_lower for term in student_locations):
            context_score += 3
            context_reasons.append(f"Location '{location}' suggests academic environment")
        
        # Tech hub locations
        tech_locations = [
            "silicon valley", "san francisco", "seattle", "austin", "boston", "new york",
            "london", "berlin", "amsterdam", "singapore", "bangalore", "nairobi"
        ]
        if any(term in location_lower for term in tech_locations):
            context_score += 2
            context_reasons.append(f"Location '{location}' is in a tech hub")
        
        # Developing regions (might indicate different pricing needs)
        developing_regions = [
            "kenya", "uganda", "tanzania", "nigeria", "ghana", "india", "pakistan",
            "bangladesh", "philippines", "indonesia", "vietnam", "thailand"
        ]
        if any(term in location_lower for term in developing_regions):
            context_score += 1
            context_reasons.append(f"Location '{location}' suggests developing region pricing needs")
    
    # Device type classification
    if device_type:
        context_sources.append("device")
        device_lower = device_type.lower()
        
        # Mobile devices might indicate different usage patterns
        if "mobile" in device_lower or "phone" in device_lower or "android" in device_lower or "ios" in device_lower:
            context_score += 1
            context_reasons.append(f"Mobile device '{device_type}' suggests on-the-go usage")
        
        # Desktop/laptop suggests professional work
        if "desktop" in device_lower or "laptop" in device_lower or "mac" in device_lower or "windows" in device_lower:
            context_score += 2
            context_reasons.append(f"Desktop/laptop '{device_type}' suggests professional work environment")
        
        # Tablet might indicate creative work
        if "tablet" in device_lower or "ipad" in device_lower:
            context_score += 1
            context_reasons.append(f"Tablet '{device_type}' suggests creative or consumption-focused usage")
    
    # Browser classification
    if browser:
        context_sources.append("browser")
        browser_lower = browser.lower()
        
        # Chrome/Safari suggests general usage
        if "chrome" in browser_lower:
            context_score += 1
            context_reasons.append("Chrome browser suggests standard web usage")
        elif "safari" in browser_lower:
            context_score += 1
            context_reasons.append("Safari browser suggests Apple ecosystem user")
        
        # Firefox might indicate tech-savvy user
        if "firefox" in browser_lower:
            context_score += 2
            context_reasons.append("Firefox browser suggests tech-savvy user")
        
        # Edge might indicate corporate environment
        if "edge" in browser_lower:
            context_score += 1
            context_reasons.append("Edge browser suggests corporate environment")
    
    # Operating system classification
    if operating_system:
        context_sources.append("os")
        os_lower = operating_system.lower()
        
        # macOS suggests creative professional or developer
        if "mac" in os_lower or "osx" in os_lower:
            context_score += 2
            context_reasons.append("macOS suggests creative professional or developer")
        
        # Windows suggests business user
        if "windows" in os_lower:
            context_score += 1
            context_reasons.append("Windows suggests business user")
        
        # Linux suggests developer or tech professional
        if "linux" in os_lower:
            context_score += 3
            context_reasons.append("Linux suggests developer or tech professional")
        
        # iOS suggests mobile-first user
        if "ios" in os_lower:
            context_score += 1
            context_reasons.append("iOS suggests mobile-first user")
    
    # Bandwidth classification
    if bandwidth_class:
        context_sources.append("bandwidth")
        bandwidth_lower = bandwidth_class.lower()
        
        # High bandwidth suggests professional or tech user
        if "high" in bandwidth_lower or "fast" in bandwidth_lower:
            context_score += 2
            context_reasons.append(f"High bandwidth '{bandwidth_class}' suggests professional environment")
        
        # Low bandwidth suggests developing region or student
        if "low" in bandwidth_lower or "slow" in bandwidth_lower:
            context_score += 1
            context_reasons.append(f"Low bandwidth '{bandwidth_class}' suggests developing region or student")
    
    # Language classification
    if language:
        context_sources.append("language")
        language_lower = language.lower()
        
        # Non-English might indicate international user
        if language_lower != "en" and language_lower != "english":
            context_score += 1
            context_reasons.append(f"Language '{language}' suggests international user")
    
    # Determine persona based on context score
    if context_score >= 5:
        persona = "tech_professional"
        confidence = "high"
    elif context_score >= 3:
        persona = "professional"
        confidence = "medium"
    elif context_score >= 1:
        persona = "general"
        confidence = "low"
    else:
        persona = "general"
        confidence = "very_low"
    
    return {
        "persona": persona,
        "confidence": confidence,
        "sources": context_sources,
        "reasoning": context_reasons,
        "context_score": context_score
    }

def get_comprehensive_persona_with_context(
    email: str,
    firecrawl_summaries: List[str],
    crawled_sources: List[str] = None,
    location: Optional[str] = None,
    device_type: Optional[str] = None,
    browser: Optional[str] = None,
    operating_system: Optional[str] = None,
    bandwidth_class: Optional[str] = None,
    language: Optional[str] = None
) -> Dict[str, any]:
    """
    Comprehensive persona classification combining email, social data, and context data.
    """
    from .persona_classifier import enhance_firecrawl_persona, classify_persona_from_email
    
    # Get email-based classification
    email_persona = classify_persona_from_email(email)
    
    # Get firecrawl-based classification
    firecrawl_result = enhance_firecrawl_persona(
        email=email,
        firecrawl_summaries=firecrawl_summaries,
        crawled_sources=crawled_sources
    )
    
    # Get context-based classification
    context_result = classify_persona_from_context(
        location=location,
        device_type=device_type,
        browser=browser,
        operating_system=operating_system,
        bandwidth_class=bandwidth_class,
        language=language
    )
    
    # Priority system: Email > Firecrawl > Context
    all_sources = []
    all_reasoning = []
    
    # Email classification (highest priority)
    if email_persona == "student":
        final_persona = "student"
        final_confidence = "high"
        all_sources.append("email")
        all_reasoning.append(f"Email domain indicates student status")
    elif email_persona:
        final_persona = email_persona
        final_confidence = "medium"
        all_sources.append("email")
        all_reasoning.append(f"Email domain analysis indicated {email_persona}")
    else:
        # Use firecrawl or context
        if firecrawl_result["persona"] != "general":
            final_persona = firecrawl_result["persona"]
            final_confidence = firecrawl_result["confidence"]
            all_sources.extend(firecrawl_result["sources"])
            all_reasoning.extend(firecrawl_result["reasoning"])
        elif context_result["context_score"] > 0:
            final_persona = context_result["persona"]
            final_confidence = context_result["confidence"]
            all_sources.extend(context_result["sources"])
            all_reasoning.extend(context_result["reasoning"])
        else:
            final_persona = "general"
            final_confidence = "very_low"
            all_sources = ["default"]
            all_reasoning = ["No specific indicators found"]
    
    return {
        "persona": final_persona,
        "confidence": final_confidence,
        "sources": list(set(all_sources)),  # Remove duplicates
        "reasoning": all_reasoning,
        "email_persona": email_persona,
        "firecrawl_persona": firecrawl_result["persona"],
        "context_persona": context_result["persona"],
        "context_score": context_result["context_score"]
    } 