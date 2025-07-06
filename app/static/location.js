// Location detection utility
class LocationDetector {
    constructor() {
        this.location = null;
        this.error = null;
    }

    // Get location using browser geolocation API
    async getCurrentLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported by this browser'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.location = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: position.timestamp
                    };
                    resolve(this.location);
                },
                (error) => {
                    this.error = error;
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5 minutes
                }
            );
        });
    }

    // Get location from IP address using a free API
    async getLocationFromIP() {
        try {
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();
            
            return {
                country: data.country_name,
                region: data.region,
                city: data.city,
                latitude: data.latitude,
                longitude: data.longitude,
                timezone: data.timezone,
                ip: data.ip
            };
        } catch (error) {
            console.error('Error getting location from IP:', error);
            return null;
        }
    }

    // Get location from IP using alternative API
    async getLocationFromIPAlternative() {
        try {
            const response = await fetch('https://api.ipgeolocation.io/ipgeo?apiKey=free');
            const data = await response.json();
            
            return {
                country: data.country_name,
                region: data.state_prov,
                city: data.city,
                latitude: data.latitude,
                longitude: data.longitude,
                timezone: data.time_zone.name,
                ip: data.ip
            };
        } catch (error) {
            console.error('Error getting location from IP (alternative):', error);
            return null;
        }
    }

    // Get location from IP using ipinfo.io (free tier)
    async getLocationFromIPInfo() {
        try {
            const response = await fetch('https://ipinfo.io/json');
            const data = await response.json();
            
            const [lat, lng] = data.loc.split(',').map(Number);
            
            return {
                country: data.country,
                region: data.region,
                city: data.city,
                latitude: lat,
                longitude: lng,
                timezone: data.timezone,
                ip: data.ip,
                org: data.org
            };
        } catch (error) {
            console.error('Error getting location from ipinfo:', error);
            return null;
        }
    }

    // Comprehensive location detection
    async detectLocation() {
        let locationData = null;

        // Try browser geolocation first (most accurate)
        try {
            const geoLocation = await this.getCurrentLocation();
            locationData = {
                method: 'browser_geolocation',
                latitude: geoLocation.latitude,
                longitude: geoLocation.longitude,
                accuracy: geoLocation.accuracy,
                timestamp: geoLocation.timestamp
            };
        } catch (error) {
            console.log('Browser geolocation failed, trying IP-based detection...');
        }

        // If browser geolocation fails, try IP-based detection
        if (!locationData) {
            try {
                locationData = await this.getLocationFromIPInfo();
                if (locationData) {
                    locationData.method = 'ip_detection';
                }
            } catch (error) {
                console.log('IP detection failed, trying alternative...');
            }
        }

        // Try alternative IP detection
        if (!locationData) {
            try {
                locationData = await this.getLocationFromIPAlternative();
                if (locationData) {
                    locationData.method = 'ip_detection_alternative';
                }
            } catch (error) {
                console.log('Alternative IP detection failed');
            }
        }

        return locationData;
    }

    // Format location for display
    formatLocation(locationData) {
        if (!locationData) return 'Unknown';

        if (locationData.city && locationData.country) {
            return `${locationData.city}, ${locationData.country}`;
        } else if (locationData.country) {
            return locationData.country;
        } else if (locationData.latitude && locationData.longitude) {
            return `${locationData.latitude.toFixed(2)}, ${locationData.longitude.toFixed(2)}`;
        }

        return 'Unknown';
    }

    // Get timezone
    getTimezone() {
        return Intl.DateTimeFormat().resolvedOptions().timeZone;
    }

    // Get language
    getLanguage() {
        return navigator.language || navigator.userLanguage || 'en';
    }
}

// Global instance
window.locationDetector = new LocationDetector();

// Auto-detect location when page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const location = await window.locationDetector.detectLocation();
        if (location) {
            // Store location in localStorage for future use
            localStorage.setItem('userLocation', JSON.stringify(location));
            
            // Send location to server if we're on a form page
            const locationInput = document.getElementById('location');
            if (locationInput) {
                locationInput.value = window.locationDetector.formatLocation(location);
            }

            // Update any location display elements
            const locationDisplays = document.querySelectorAll('.location-display');
            locationDisplays.forEach(element => {
                element.textContent = window.locationDetector.formatLocation(location);
            });
        }
    } catch (error) {
        console.error('Location detection failed:', error);
    }
}); 