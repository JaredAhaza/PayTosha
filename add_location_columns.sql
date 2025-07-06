-- Add new location and context columns to context_profiles table
-- This migration adds the enhanced location detection fields

-- Add new location-related columns
ALTER TABLE context_profiles 
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS region VARCHAR(100),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50),
ADD COLUMN IF NOT EXISTS coordinates JSONB,
ADD COLUMN IF NOT EXISTS ip_address INET,
ADD COLUMN IF NOT EXISTS time_of_day VARCHAR(20),
ADD COLUMN IF NOT EXISTS day_of_week VARCHAR(20),
ADD COLUMN IF NOT EXISTS is_weekend BOOLEAN DEFAULT FALSE;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_context_profiles_country ON context_profiles(country);
CREATE INDEX IF NOT EXISTS idx_context_profiles_city ON context_profiles(city);
CREATE INDEX IF NOT EXISTS idx_context_profiles_timezone ON context_profiles(timezone);
CREATE INDEX IF NOT EXISTS idx_context_profiles_time_of_day ON context_profiles(time_of_day);

-- Update existing records to have default values
UPDATE context_profiles 
SET 
    country = 'Unknown',
    region = 'Unknown', 
    city = 'Unknown',
    timezone = 'UTC',
    time_of_day = 'unknown',
    day_of_week = 'unknown',
    is_weekend = FALSE
WHERE country IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN context_profiles.country IS 'User country detected from IP or geolocation';
COMMENT ON COLUMN context_profiles.region IS 'User region/state detected from IP or geolocation';
COMMENT ON COLUMN context_profiles.city IS 'User city detected from IP or geolocation';
COMMENT ON COLUMN context_profiles.timezone IS 'User timezone detected from IP or geolocation';
COMMENT ON COLUMN context_profiles.coordinates IS 'Latitude and longitude coordinates as JSON';
COMMENT ON COLUMN context_profiles.ip_address IS 'User IP address for location detection';
COMMENT ON COLUMN context_profiles.time_of_day IS 'Time of day: morning, afternoon, evening, night';
COMMENT ON COLUMN context_profiles.day_of_week IS 'Day of week: monday, tuesday, etc.';
COMMENT ON COLUMN context_profiles.is_weekend IS 'Whether the current day is a weekend'; 