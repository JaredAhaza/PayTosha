import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
import json

# Lingo.dev API configuration
LINGO_API_KEY = "api_kayrnb27wkyct7ny2jjyshan"
LINGO_API_BASE_URL = "https://api.lingo.dev/v1"

class LanguageService:
    def __init__(self):
        self.api_key = LINGO_API_KEY
        self.base_url = LINGO_API_BASE_URL
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of given text"""
        try:
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text
            }
            
            async with session.post(
                f"{self.base_url}/detect",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("language", "en")
                else:
                    print(f"Language detection failed: {response.status}")
                    return "en"
        except Exception as e:
            print(f"Error detecting language: {e}")
            return "en"
    
    async def translate_text(self, text: str, target_language: str, source_language: str = "en") -> str:
        """Translate text to target language"""
        try:
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "sourceLanguage": source_language,
                "targetLanguage": target_language
            }
            
            async with session.post(
                f"{self.base_url}/translate",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("translatedText", text)
                else:
                    print(f"Translation failed: {response.status}")
                    return text
        except Exception as e:
            print(f"Error translating text: {e}")
            return text
    
    async def translate_dict(self, data: Dict[str, Any], target_language: str, source_language: str = "en") -> Dict[str, Any]:
        """Translate all string values in a dictionary"""
        if target_language == source_language:
            return data
        
        translated_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                translated_data[key] = await self.translate_text(value, target_language, source_language)
            elif isinstance(value, dict):
                translated_data[key] = await self.translate_dict(value, target_language, source_language)
            elif isinstance(value, list):
                translated_data[key] = []
                for item in value:
                    if isinstance(item, str):
                        translated_data[key].append(await self.translate_text(item, target_language, source_language))
                    elif isinstance(item, dict):
                        translated_data[key].append(await self.translate_dict(item, target_language, source_language))
                    else:
                        translated_data[key].append(item)
            else:
                translated_data[key] = value
        
        return translated_data
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global language service instance
language_service = LanguageService()

# Common translations for PayTosha
COMMON_TRANSLATIONS = {
    "en": {
        # Core navigation
        "welcome": "Welcome",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "marketplace": "Marketplace",
        "packages": "Packages",
        "profile": "Profile",
        "settings": "Settings",
        "search": "Search",
        "buy": "Buy",
        "sell": "Sell",
        "price": "Price",
        "description": "Description",
        "category": "Category",
        "fair_pricing": "Fair Pricing",
        "student_discount": "Student Discount",
        "premium_features": "Premium Features",
        "free_plan": "Free Plan",
        "premium_plan": "Premium Plan",
        "enterprise_plan": "Enterprise Plan",
        
        # Landing page
        "paytosha_title": "PayTosha",
        "tagline": "Context-Aware Fair Pricing Platform",
        "get_started": "Get Started",
        "learn_more": "Learn More",
        
        # Login page
        "login_title": "Login to PayTosha",
        "email_address": "Email Address",
        "password": "Password",
        "remember_me": "Remember Me",
        "forgot_password": "Forgot Password?",
        "dont_have_account": "Don't have an account?",
        "sign_up": "Sign Up",
        
        # Register page
        "register_title": "Create Your Account",
        "first_name": "First Name",
        "last_name": "Last Name",
        "confirm_password": "Confirm Password",
        "already_have_account": "Already have an account?",
        "sign_in": "Sign In",
        "terms_agreement": "I agree to the Terms of Service and Privacy Policy",
        
        # Marketplace
        "browse_products": "Browse Products",
        "filter_by_category": "Filter by Category",
        "all_categories": "All Categories",
        "sort_by": "Sort by",
        "price_low_high": "Price: Low to High",
        "price_high_low": "Price: High to Low",
        "newest_first": "Newest First",
        "add_to_cart": "Add to Cart",
        "view_details": "View Details",
        "out_of_stock": "Out of Stock",
        "in_stock": "In Stock",
        "product_details": "Product Details",
        "quantity": "Quantity",
        "total_price": "Total Price",
        "checkout": "Checkout",
        "continue_shopping": "Continue Shopping",
        "related_products": "Related Products",
        
        # Packages
        "package_dashboard": "Package Dashboard",
        "current_package": "Current Package",
        "upgrade_package": "Upgrade Package",
        "downgrade_package": "Downgrade Package",
        "cancel_package": "Cancel Package",
        "package_features": "Package Features",
        "monthly_billing": "Monthly Billing",
        "annual_billing": "Annual Billing",
        "billing_cycle": "Billing Cycle",
        "next_billing_date": "Next Billing Date",
        "payment_method": "Payment Method",
        "update_payment": "Update Payment",
        "billing_history": "Billing History",
        "invoice": "Invoice",
        "download_invoice": "Download Invoice",
        
        # Orders
        "my_orders": "My Orders",
        "order_history": "Order History",
        "order_number": "Order Number",
        "order_date": "Order Date",
        "order_status": "Order Status",
        "order_total": "Order Total",
        "pending": "Pending",
        "processing": "Processing",
        "shipped": "Shipped",
        "delivered": "Delivered",
        "cancelled": "Cancelled",
        "track_order": "Track Order",
        "order_details": "Order Details",
        
        # Dashboard specific
        "overview": "Overview",
        "analytics": "Analytics",
        "recent_activity": "Recent Activity",
        "quick_actions": "Quick Actions",
        "notifications": "Notifications",
        "help_support": "Help & Support",
        
        # Common actions
        "save": "Save",
        "cancel": "Cancel",
        "edit": "Edit",
        "delete": "Delete",
        "update": "Update",
        "create": "Create",
        "submit": "Submit",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "close": "Close",
        "confirm": "Confirm",
        "yes": "Yes",
        "no": "No",
        
        # Status messages
        "loading": "Loading...",
        "success": "Success!",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "processing": "Processing...",
        "please_wait": "Please wait...",
        
        # Time and dates
        "today": "Today",
        "yesterday": "Yesterday",
        "this_week": "This Week",
        "this_month": "This Month",
        "last_month": "Last Month",
        
        # Currency and numbers
        "currency": "USD",
        "free": "Free",
        "discount": "Discount",
        "tax": "Tax",
        "shipping": "Shipping",
        "total": "Total",
        "subtotal": "Subtotal",
        # Welcome page specific translations
        "account_info": "Account Info",
        "full_name": "Full Name",
        "username": "Username",
        "email": "Email",
        "account_created": "Account Created At",
        "location_context": "Location & Context",
        "location": "Location",
        "country": "Country",
        "city": "City",
        "timezone": "Timezone",
        "time_of_day": "Time of Day",
        "coordinates": "Coordinates",
        "mobile_optimized": "Mobile-optimized experience activated",
        "desktop_experience": "Full desktop experience available",
        "using_browser": "Using",
        "on_os": "on",
        "smart_insights": "Smart Insights",
        "persona_guess": "Persona Guess",
        "confidence": "Confidence",
        "sources": "Sources",
        "reasoning": "Reasoning",
        "student_resources": "Student Resources",
        "student_verification_required": "Student verification required for discount",
        "access_educational_tools": "Access to educational tools and resources",
        "limited_usage_student": "Limited usage with student benefits",
        "developer_tools": "Developer Tools",
        "advanced_analytics": "Advanced analytics and integrations",
        "api_access": "API access and developer documentation",
        "priority_support": "Priority support for technical issues",
        "freelancer_tools": "Freelancer Tools",
        "project_management": "Project management features",
        "client_billing": "Client billing and invoicing tools",
        "portfolio_showcase": "Portfolio showcase capabilities",
        "entrepreneur_features": "Entrepreneur Features",
        "business_analytics": "Business analytics and insights",
        "team_management": "Team management tools",
        "growth_tracking": "Growth tracking and metrics",
        "dynamic_pricing": "Dynamic Pricing",
        "income_level": "Income Level",
        "suggested_tier": "Suggested Tier",
        "package_assigned": "Package Automatically Assigned!",
        "package_assigned_desc": "Your package has been automatically assigned based on your profile analysis.",
        "manage_package": "Manage Package",
        "premium_plan_title": "Premium Plan",
        "premium_plan_desc": "All features unlocked • Priority support • Advanced analytics",
        "student_plan_title": "Student Plan (70% OFF)",
        "student_plan_desc": "Student verification required • Basic features • Limited usage",
        "fair_plan_title": "Fair Plan (50% OFF)",
        "fair_plan_desc": "Regional pricing • Core features • Community support",
        "free_plan_title": "Free Plan (100% OFF)",
        "free_plan_desc": "Basic features • Limited usage • Community support",
        "standard_plan_title": "Standard Plan",
        "standard_plan_desc": "All features • Standard support • Regular updates",
        "low_bandwidth_mode": "Low Bandwidth Mode",
        "low_bandwidth_desc": "Optimized for slower connections • Reduced media loading • Lightweight interface",
        "high_performance_mode": "High Performance Mode",
        "high_performance_desc": "Full media experience • Real-time updates • Advanced animations",
        "social_summary": "Social Summary",
        "no_social_data": "No social data was crawled.",
        "browse_marketplace": "Browse Marketplace",
        "discover_products": "Discover products with fair, context-aware pricing",
        "upgrade_premium": "Upgrade to Premium",
        "unlock_features": "Unlock all features and get priority support",
        "complete_verification": "Complete Student Verification",
        "verify_student": "Verify your student status to maintain discount",
        "access_premium_dashboard": "Access Premium Dashboard",
        "explore_features": "Explore advanced features and analytics",
        "go_to_dashboard": "Go to Dashboard",
        "start_exploring": "Start exploring your personalized experience",
        "mobile_optimized_exp": "Mobile-optimized experience • Swipe-friendly interface",
        "desktop_full_exp": "Full desktop experience • Keyboard shortcuts available",
        "detecting": "Detecting...",
        "unknown": "Unknown",
        "no_summary": "No summary available",
        "source": "Source"
    },
    "sw": {
        # Core navigation
        "welcome": "Karibu",
        "login": "Ingia",
        "register": "Jisajili",
        "logout": "Ondoka",
        "dashboard": "Dashibodi",
        "marketplace": "Soko",
        "packages": "Mifuko",
        "profile": "Wasifu",
        "settings": "Mipangilio",
        "search": "Tafuta",
        "buy": "Nunua",
        "sell": "Uza",
        "price": "Bei",
        "description": "Maelezo",
        "category": "Kategoria",
        "fair_pricing": "Bei Haki",
        "student_discount": "Punguzo la Mwanafunzi",
        "premium_features": "Vipengele vya Premium",
        "free_plan": "Mpango wa Bure",
        "premium_plan": "Mpango wa Premium",
        "enterprise_plan": "Mpango wa Biashara",
        
        # Landing page
        "paytosha_title": "PayTosha",
        "tagline": "Jukwaa la Bei Haki ya Mazingira",
        "get_started": "Anza",
        "learn_more": "Jifunze Zaidi",
        
        # Login page
        "login_title": "Ingia kwenye PayTosha",
        "email_address": "Anwani ya Barua Pepe",
        "password": "Nywila",
        "remember_me": "Nikumbuke",
        "forgot_password": "Umesahau nywila?",
        "dont_have_account": "Huna akaunti?",
        "sign_up": "Jisajili",
        
        # Register page
        "register_title": "Unda Akaunti Yako",
        "first_name": "Jina la Kwanza",
        "last_name": "Jina la Mwisho",
        "confirm_password": "Thibitisha Nywila",
        "already_have_account": "Una akaunti tayari?",
        "sign_in": "Ingia",
        "terms_agreement": "Nakubaliana na Sheria za Huduma na Sera ya Faragha",
        
        # Marketplace
        "browse_products": "Tafuta Bidhaa",
        "filter_by_category": "Chuja kwa Kategoria",
        "all_categories": "Kategoria Zote",
        "sort_by": "Panga kwa",
        "price_low_high": "Bei: Chini hadi Juu",
        "price_high_low": "Bei: Juu hadi Chini",
        "newest_first": "Mpya Kwanza",
        "add_to_cart": "Ongeza kwenye Cart",
        "view_details": "Ona Maelezo",
        "out_of_stock": "Hakuna Hifadhi",
        "in_stock": "Iko Hifadhi",
        "product_details": "Maelezo ya Bidhaa",
        "quantity": "Idadi",
        "total_price": "Bei ya Jumla",
        "checkout": "Malipo",
        "continue_shopping": "Endelea Kununua",
        "related_products": "Bidhaa Zinazohusiana",
        
        # Packages
        "package_dashboard": "Dashibodi ya Mifuko",
        "current_package": "Mfuko wa Sasa",
        "upgrade_package": "Boresha Mfuko",
        "downgrade_package": "Punguza Mfuko",
        "cancel_package": "Ghairi Mfuko",
        "package_features": "Vipengele vya Mfuko",
        "monthly_billing": "Bili ya Mwezi",
        "annual_billing": "Bili ya Mwaka",
        "billing_cycle": "Mzunguko wa Bili",
        "next_billing_date": "Tarehe ya Bili Inayofuata",
        "payment_method": "Njia ya Malipo",
        "update_payment": "Sasisha Malipo",
        "billing_history": "Historia ya Bili",
        "invoice": "Ankara",
        "download_invoice": "Pakua Ankara",
        
        # Orders
        "my_orders": "Oda Zangu",
        "order_history": "Historia ya Oda",
        "order_number": "Nambari ya Oda",
        "order_date": "Tarehe ya Oda",
        "order_status": "Hali ya Oda",
        "order_total": "Jumla ya Oda",
        "pending": "Inasubiri",
        "processing": "Inachakata",
        "shipped": "Imetumwa",
        "delivered": "Imeletwa",
        "cancelled": "Imekatwa",
        "track_order": "Fuatilia Oda",
        "order_details": "Maelezo ya Oda",
        
        # Dashboard specific
        "overview": "Muhtasari",
        "analytics": "Uchambuzi",
        "recent_activity": "Shughuli za Hivi Karibuni",
        "quick_actions": "Vitendo vya Haraka",
        "notifications": "Arifa",
        "help_support": "Msaada & Usaidizi",
        
        # Common actions
        "save": "Hifadhi",
        "cancel": "Ghairi",
        "edit": "Hariri",
        "delete": "Futa",
        "update": "Sasisha",
        "create": "Unda",
        "submit": "Wasilisha",
        "back": "Rudi",
        "next": "Ifuatayo",
        "previous": "Iliyotangulia",
        "close": "Funga",
        "confirm": "Thibitisha",
        "yes": "Ndiyo",
        "no": "Hapana",
        
        # Status messages
        "loading": "Inapakia...",
        "success": "Imefanikiwa!",
        "error": "Hitilafu",
        "warning": "Onyo",
        "info": "Maelezo",
        "processing": "Inachakata...",
        "please_wait": "Tafadhali subiri...",
        
        # Time and dates
        "today": "Leo",
        "yesterday": "Jana",
        "this_week": "Wiki Hii",
        "this_month": "Mwezi Huu",
        "last_month": "Mwezi Uliopita",
        
        # Currency and numbers
        "currency": "USD",
        "free": "Bure",
        "discount": "Punguzo",
        "tax": "Kodi",
        "shipping": "Usambazaji",
        "total": "Jumla",
        "subtotal": "Jumla ndogo",
        # Welcome page specific translations
        "account_info": "Maelezo ya Akaunti",
        "full_name": "Jina Kamili",
        "username": "Jina la Mtumiaji",
        "email": "Barua Pepe",
        "account_created": "Akaunti Iliundwa",
        "location_context": "Mahali na Mazingira",
        "location": "Mahali",
        "country": "Nchi",
        "city": "Jiji",
        "timezone": "Muda wa Eneo",
        "time_of_day": "Muda wa Siku",
        "coordinates": "Viweko",
        "mobile_optimized": "Uzoefu wa simu ulioboreshwa umewezeshwa",
        "desktop_experience": "Uzoefu kamili wa kompyuta unapatikana",
        "using_browser": "Kutumia",
        "on_os": "kwenye",
        "smart_insights": "Ufahamu wa Busara",
        "persona_guess": "Dhana ya Mtu",
        "confidence": "Uthibitisho",
        "sources": "Vyanzo",
        "reasoning": "Sababu",
        "student_resources": "Rasilimali za Mwanafunzi",
        "student_verification_required": "Uthibitisho wa mwanafunzi unahitajika kwa punguzo",
        "access_educational_tools": "Ufikiaji wa zana na rasilimali za elimu",
        "limited_usage_student": "Matumizi ya kikomo na faida za mwanafunzi",
        "developer_tools": "Zana za Mwendelezi",
        "advanced_analytics": "Uchambuzi wa hali ya juu na ujumuishaji",
        "api_access": "Ufikiaji wa API na nyaraka za mwendelezi",
        "priority_support": "Msaada wa kipaumbele kwa matatizo ya kiufundi",
        "freelancer_tools": "Zana za Mfanyakazi wa Kujitegemea",
        "project_management": "Vipengele vya usimamizi wa miradi",
        "client_billing": "Zana za bili na ankara za mteja",
        "portfolio_showcase": "Uwezo wa kuonyesha portfolio",
        "entrepreneur_features": "Vipengele vya Mjasiriamali",
        "business_analytics": "Uchambuzi wa biashara na ufahamu",
        "team_management": "Zana za usimamizi wa timu",
        "growth_tracking": "Ufuatiliaji wa ukuaji na vipimo",
        "dynamic_pricing": "Bei ya Mabadiliko",
        "income_level": "Kiwango cha Mapato",
        "suggested_tier": "Kiwango Kilichopendekezwa",
        "package_assigned": "Mfuko Umepewa Kiotomatiki!",
        "package_assigned_desc": "Mfuko wako umepewa kiotomatiki kulingana na uchambuzi wa wasifu wako.",
        "manage_package": "Simamia Mfuko",
        "premium_plan_title": "Mpango wa Premium",
        "premium_plan_desc": "Vipengele vyote vimefunguliwa • Msaada wa kipaumbele • Uchambuzi wa hali ya juu",
        "student_plan_title": "Mpango wa Mwanafunzi (70% PUNGUZO)",
        "student_plan_desc": "Uthibitisho wa mwanafunzi unahitajika • Vipengele vya msingi • Matumizi ya kikomo",
        "fair_plan_title": "Mpango wa Haki (50% PUNGUZO)",
        "fair_plan_desc": "Bei ya kikanda • Vipengele vya msingi • Msaada wa jamii",
        "free_plan_title": "Mpango wa Bure (100% PUNGUZO)",
        "free_plan_desc": "Vipengele vya msingi • Matumizi ya kikomo • Msaada wa jamii",
        "standard_plan_title": "Mpango wa Kawaida",
        "standard_plan_desc": "Vipengele vyote • Msaada wa kawaida • Vipimo vya kawaida",
        "low_bandwidth_mode": "Hali ya Bandwidth ya Chini",
        "low_bandwidth_desc": "Iliyoboreshwa kwa miunganisho ya polepole • Kupakia media kupunguzwa • Interface nyepesi",
        "high_performance_mode": "Hali ya Utendaji wa Juu",
        "high_performance_desc": "Uzoefu kamili wa media • Vipimo vya wakati halisi • Animations za hali ya juu",
        "social_summary": "Muhtasari wa Kijamii",
        "no_social_data": "Hakuna data ya kijamii iliyopigwa.",
        "browse_marketplace": "Tafuta Soko",
        "discover_products": "Gundua bidhaa na bei ya haki, inayojua mazingira",
        "upgrade_premium": "Boresha kwa Premium",
        "unlock_features": "Fungua vipengele vyote na upate msaada wa kipaumbele",
        "complete_verification": "Kamilisha Uthibitisho wa Mwanafunzi",
        "verify_student": "Thibitisha hali yako ya mwanafunzi kudumisha punguzo",
        "access_premium_dashboard": "Fikia Dashibodi ya Premium",
        "explore_features": "Chunguza vipengele vya hali ya juu na uchambuzi",
        "go_to_dashboard": "Nenda kwenye Dashibodi",
        "start_exploring": "Anza kuchunguza uzoefu wako wa kibinafsi",
        "mobile_optimized_exp": "Uzoefu wa simu ulioboreshwa • Interface rahisi kwa swipe",
        "desktop_full_exp": "Uzoefu kamili wa kompyuta • Shortcuts za kibodi zinapatikana",
        "detecting": "Inagundua...",
        "unknown": "Haijulikani",
        "no_summary": "Hakuna muhtasari unaopatikana",
        "source": "Chanzo"
    }
}

def get_translation(key: str, language: str = "en") -> str:
    """Get translation for a common key"""
    return COMMON_TRANSLATIONS.get(language, COMMON_TRANSLATIONS["en"]).get(key, key)

def get_all_translations(language: str = "en") -> dict:
    """Get all translations for a given language"""
    return COMMON_TRANSLATIONS.get(language, COMMON_TRANSLATIONS["en"])

def detect_user_language_from_context(context_profile) -> str:
    """Detect user's preferred language from context profile"""
    if not context_profile:
        return "en"
    
    # Check location for language preference
    country = getattr(context_profile, 'country', '').lower()
    
    # Map countries to languages
    country_language_map = {
        'kenya': 'sw',
        'tanzania': 'sw',
        'uganda': 'sw',
        'rwanda': 'sw',
        'burundi': 'sw',
        'somalia': 'so',
        'ethiopia': 'am',
        'south africa': 'af',
        'nigeria': 'yo',
        'ghana': 'tw',
        'senegal': 'wo',
        'mali': 'bm',
        'morocco': 'ar',
        'egypt': 'ar',
        'tunisia': 'ar',
        'algeria': 'ar'
    }
    
    return country_language_map.get(country, 'en')

async def translate_dynamic_content(text: str, target_language: str, source_language: str = "en") -> str:
    """Translate dynamic content using Lingo.dev API"""
    if target_language == source_language or not text:
        return text
    
    try:
        # Use Lingo.dev API to translate the text
        translated = await language_service.translate_text(text, target_language, source_language)
        print(f"🌐 Translated '{text}' to '{translated}' ({source_language} -> {target_language})")
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text

async def translate_page_content(content_dict: dict, target_language: str, source_language: str = "en") -> dict:
    """Translate all text content in a dictionary using Lingo.dev"""
    if target_language == source_language:
        return content_dict
    
    translated_dict = {}
    
    for key, value in content_dict.items():
        if isinstance(value, str) and value.strip():
            # Skip translation keys and technical terms
            if key.startswith('translations_') or key in ['user_language', 'request']:
                translated_dict[key] = value
            else:
                translated_dict[key] = await translate_dynamic_content(value, target_language, source_language)
        elif isinstance(value, dict):
            translated_dict[key] = await translate_page_content(value, target_language, source_language)
        elif isinstance(value, list):
            translated_list = []
            for item in value:
                if isinstance(item, str):
                    translated_list.append(await translate_dynamic_content(item, target_language, source_language))
                elif isinstance(item, dict):
                    translated_list.append(await translate_page_content(item, target_language, source_language))
                else:
                    translated_list.append(item)
            translated_dict[key] = translated_list
        else:
            translated_dict[key] = value
    
    return translated_dict

async def translate_welcome_page_content(user_data: dict, context_data: dict, target_language: str) -> dict:
    """Translate all dynamic content on the welcome page"""
    if target_language == "en":
        return {
            "user": user_data,
            "context": context_data
        }
    
    try:
        # Translate user data
        translated_user = user_data.copy()
        if user_data.get("first_name"):
            translated_user["first_name"] = await translate_dynamic_content(
                user_data["first_name"], target_language
            )
        if user_data.get("last_name"):
            translated_user["last_name"] = await translate_dynamic_content(
                user_data["last_name"], target_language
            )
        
        # Translate context data
        translated_context = context_data.copy()
        if context_data.get("location"):
            translated_context["location"] = await translate_dynamic_content(
                context_data["location"], target_language
            )
        if context_data.get("city"):
            translated_context["city"] = await translate_dynamic_content(
                context_data["city"], target_language
            )
        if context_data.get("country"):
            translated_context["country"] = await translate_dynamic_content(
                context_data["country"], target_language
            )
        
        # Translate persona reasoning if available
        if context_data.get("persona_reasoning"):
            translated_reasoning = []
            for reason in context_data["persona_reasoning"]:
                translated_reasoning.append(
                    await translate_dynamic_content(reason, target_language)
                )
            translated_context["persona_reasoning"] = translated_reasoning
        
        # Translate social data if available
        if context_data.get("social_data"):
            translated_social = []
            for social_item in context_data["social_data"]:
                translated_item = social_item.copy()
                if social_item.get("firecrawl_ai_summary"):
                    translated_item["firecrawl_ai_summary"] = await translate_dynamic_content(
                        social_item["firecrawl_ai_summary"], target_language
                    )
                if social_item.get("source"):
                    translated_item["source"] = await translate_dynamic_content(
                        social_item["source"], target_language
                    )
                translated_social.append(translated_item)
            translated_context["social_data"] = translated_social
        
        return {
            "user": translated_user,
            "context": translated_context
        }
        
    except Exception as e:
        print(f"Error translating welcome page content: {e}")
        return {
            "user": user_data,
            "context": context_data
        } 