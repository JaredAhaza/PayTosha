import requests
import json
from typing import Optional, Dict, Any
import logging

class GeolocationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_location_from_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get location information from IP address using multiple free APIs
        """
        # Try ipinfo.io first (most reliable free tier)
        location = self._get_from_ipinfo(ip_address)
        if location:
            return location
        
        # Try ipapi.co as backup
        location = self._get_from_ipapi(ip_address)
        if location:
            return location
        
        # Try ipgeolocation.io as last resort
        location = self._get_from_ipgeolocation(ip_address)
        if location:
            return location
        
        return None
    
    def _get_from_ipinfo(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get location from ipinfo.io"""
        try:
            url = f"https://ipinfo.io/{ip_address}/json"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Parse location coordinates
            lat, lng = None, None
            if 'loc' in data:
                try:
                    lat, lng = map(float, data['loc'].split(','))
                except (ValueError, AttributeError):
                    pass
            
            return {
                'country': data.get('country'),
                'region': data.get('region'),
                'city': data.get('city'),
                'latitude': lat,
                'longitude': lng,
                'timezone': data.get('timezone'),
                'ip': data.get('ip'),
                'org': data.get('org'),
                'source': 'ipinfo.io'
            }
        except Exception as e:
            self.logger.warning(f"ipinfo.io failed: {e}")
            return None
    
    def _get_from_ipapi(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get location from ipapi.co"""
        try:
            url = f"https://ipapi.co/{ip_address}/json/"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return {
                'country': data.get('country_name'),
                'region': data.get('region'),
                'city': data.get('city'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone'),
                'ip': data.get('ip'),
                'source': 'ipapi.co'
            }
        except Exception as e:
            self.logger.warning(f"ipapi.co failed: {e}")
            return None
    
    def _get_from_ipgeolocation(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get location from ipgeolocation.io"""
        try:
            url = f"https://api.ipgeolocation.io/ipgeo?apiKey=free&ip={ip_address}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return {
                'country': data.get('country_name'),
                'region': data.get('state_prov'),
                'city': data.get('city'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('time_zone', {}).get('name'),
                'ip': data.get('ip'),
                'source': 'ipgeolocation.io'
            }
        except Exception as e:
            self.logger.warning(f"ipgeolocation.io failed: {e}")
            return None
    
    def get_client_ip(self, request) -> str:
        """
        Extract client IP address from request
        """
        # Check for forwarded headers (common with proxies)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Check for client IP header
        client_ip = request.headers.get('X-Client-IP')
        if client_ip:
            return client_ip
        
        # Fallback to remote address
        return request.client.host if request.client else '127.0.0.1'
    
    def format_location_display(self, location_data: Dict[str, Any]) -> str:
        """
        Format location data for display
        """
        if not location_data:
            return 'Unknown'
        
        city = location_data.get('city')
        country = location_data.get('country')
        
        if city and country:
            return f"{city}, {country}"
        elif country:
            return country
        elif location_data.get('latitude') and location_data.get('longitude'):
            lat = location_data['latitude']
            lng = location_data['longitude']
            return f"{lat:.2f}, {lng:.2f}"
        
        return 'Unknown'
    
    def get_location_summary(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of location data for context analysis
        """
        if not location_data:
            return {
                'location': 'Unknown',
                'country': 'Unknown',
                'region': 'Unknown',
                'city': 'Unknown',
                'timezone': 'Unknown',
                'coordinates': None
            }
        
        return {
            'location': self.format_location_display(location_data),
            'country': location_data.get('country', 'Unknown'),
            'region': location_data.get('region', 'Unknown'),
            'city': location_data.get('city', 'Unknown'),
            'timezone': location_data.get('timezone', 'Unknown'),
            'coordinates': {
                'latitude': location_data.get('latitude'),
                'longitude': location_data.get('longitude')
            } if location_data.get('latitude') and location_data.get('longitude') else None
        }

# Global instance
geolocation_service = GeolocationService() 