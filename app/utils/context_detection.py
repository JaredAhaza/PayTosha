import re
from typing import Dict, Any, Optional
from .geolocation import geolocation_service

class ContextDetector:
    def __init__(self):
        self.user_agent_patterns = {
            'mobile': [
                r'Android', r'iPhone', r'iPad', r'Mobile', r'BlackBerry',
                r'Windows Phone', r'Opera Mini', r'IEMobile'
            ],
            'desktop': [
                r'Windows NT', r'Macintosh', r'Linux', r'X11'
            ],
            'browser': {
                'chrome': r'Chrome',
                'firefox': r'Firefox',
                'safari': r'Safari',
                'edge': r'Edge',
                'opera': r'Opera'
            },
            'os': {
                'windows': r'Windows NT',
                'macos': r'Macintosh',
                'linux': r'Linux',
                'android': r'Android',
                'ios': r'iPhone|iPad'
            }
        }
    
    def detect_device_info(self, user_agent: str) -> Dict[str, str]:
        """
        Detect device information from User-Agent string
        """
        user_agent = user_agent.lower()
        
        # Detect device type
        device_type = 'desktop'
        for pattern in self.user_agent_patterns['mobile']:
            if re.search(pattern, user_agent, re.IGNORECASE):
                device_type = 'mobile'
                break
        
        # Detect browser
        browser = 'unknown'
        for browser_name, pattern in self.user_agent_patterns['browser'].items():
            if re.search(pattern, user_agent, re.IGNORECASE):
                browser = browser_name
                break
        
        # Detect OS
        os_name = 'unknown'
        for os_name_key, pattern in self.user_agent_patterns['os'].items():
            if re.search(pattern, user_agent, re.IGNORECASE):
                os_name = os_name_key
                break
        
        return {
            'device_type': device_type,
            'browser': browser,
            'os': os_name
        }
    
    def detect_location(self, request) -> Dict[str, Any]:
        """
        Detect user location using multiple methods
        """
        # Get client IP
        client_ip = geolocation_service.get_client_ip(request)
        
        # Get location from IP
        location_data = geolocation_service.get_location_from_ip(client_ip)
        
        # Format for display
        location_display = geolocation_service.format_location_display(location_data)
        
        return {
            'ip': client_ip,
            'location': location_display,
            'location_data': location_data,
            'country': location_data.get('country') if location_data else 'Unknown',
            'region': location_data.get('region') if location_data else 'Unknown',
            'city': location_data.get('city') if location_data else 'Unknown',
            'timezone': location_data.get('timezone') if location_data else 'Unknown',
            'coordinates': {
                'latitude': location_data.get('latitude'),
                'longitude': location_data.get('longitude')
            } if location_data and location_data.get('latitude') else None
        }
    
    def detect_time_context(self) -> Dict[str, Any]:
        """
        Detect time-based context
        """
        from datetime import datetime
        import pytz
        
        now = datetime.now()
        
        # Get timezone from system or default to UTC
        try:
            timezone = pytz.timezone('UTC')  # Default
        except:
            timezone = pytz.UTC
        
        # Determine time of day
        hour = now.hour
        if 6 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= hour < 21:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        
        # Determine day of week
        day_of_week = now.strftime('%A').lower()
        
        # Determine if weekend
        is_weekend = day_of_week in ['saturday', 'sunday']
        
        return {
            'hour': hour,
            'time_of_day': time_of_day,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'timestamp': now.isoformat(),
            'timezone': str(timezone)
        }
    
    def detect_language(self, request) -> str:
        """
        Detect user's preferred language
        """
        # Check Accept-Language header
        accept_language = request.headers.get('Accept-Language', '')
        if accept_language:
            # Parse the first language preference
            primary_lang = accept_language.split(',')[0].split(';')[0].strip()
            return primary_lang
        
        return 'en'  # Default to English
    
    def get_comprehensive_context(self, request) -> Dict[str, Any]:
        """
        Get comprehensive context information for a request
        """
        user_agent = request.headers.get('User-Agent', '')
        
        # Detect all context information
        device_info = self.detect_device_info(user_agent)
        location_info = self.detect_location(request)
        time_context = self.detect_time_context()
        language = self.detect_language(request)
        
        # Combine all context
        context = {
            # Device information
            'device_type': device_info['device_type'],
            'browser': device_info['browser'],
            'os': device_info['os'],
            
            # Location information
            'location': location_info['location'],
            'country': location_info['country'],
            'region': location_info['region'],
            'city': location_info['city'],
            'timezone': location_info['timezone'],
            'coordinates': location_info['coordinates'],
            'ip': location_info['ip'],
            
            # Time context
            'time_of_day': time_context['time_of_day'],
            'day_of_week': time_context['day_of_week'],
            'is_weekend': time_context['is_weekend'],
            'hour': time_context['hour'],
            
            # Language
            'language': language,
            
            # Raw data for advanced analysis
            'raw_location_data': location_info['location_data'],
            'raw_time_data': time_context
        }
        
        return context
    
    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of the context
        """
        parts = []
        
        # Device info
        parts.append(f"{context['device_type'].title()} user")
        parts.append(f"on {context['browser'].title()}")
        parts.append(f"({context['os'].title()})")
        
        # Location
        if context['location'] != 'Unknown':
            parts.append(f"from {context['location']}")
        
        # Time context
        parts.append(f"during {context['time_of_day']}")
        if context['is_weekend']:
            parts.append("on weekend")
        
        return " ".join(parts)

# Global instance
context_detector = ContextDetector()
