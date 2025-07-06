-- Simple migration to add location columns to context_profiles
-- This handles cases where some columns might already exist

DO $$ 
BEGIN
    -- Add country column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'country') THEN
        ALTER TABLE context_profiles ADD COLUMN country VARCHAR(100);
    END IF;
    
    -- Add region column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'region') THEN
        ALTER TABLE context_profiles ADD COLUMN region VARCHAR(100);
    END IF;
    
    -- Add city column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'city') THEN
        ALTER TABLE context_profiles ADD COLUMN city VARCHAR(100);
    END IF;
    
    -- Add timezone column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'timezone') THEN
        ALTER TABLE context_profiles ADD COLUMN timezone VARCHAR(50);
    END IF;
    
    -- Add coordinates column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'coordinates') THEN
        ALTER TABLE context_profiles ADD COLUMN coordinates JSONB;
    END IF;
    
    -- Add ip_address column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'ip_address') THEN
        ALTER TABLE context_profiles ADD COLUMN ip_address VARCHAR(45); -- INET type as VARCHAR for compatibility
    END IF;
    
    -- Add time_of_day column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'time_of_day') THEN
        ALTER TABLE context_profiles ADD COLUMN time_of_day VARCHAR(20);
    END IF;
    
    -- Add day_of_week column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'day_of_week') THEN
        ALTER TABLE context_profiles ADD COLUMN day_of_week VARCHAR(20);
    END IF;
    
    -- Add is_weekend column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'context_profiles' AND column_name = 'is_weekend') THEN
        ALTER TABLE context_profiles ADD COLUMN is_weekend BOOLEAN DEFAULT FALSE;
    END IF;
    
END $$;

-- Update existing records with default values
UPDATE context_profiles 
SET 
    country = COALESCE(country, 'Unknown'),
    region = COALESCE(region, 'Unknown'),
    city = COALESCE(city, 'Unknown'),
    timezone = COALESCE(timezone, 'UTC'),
    time_of_day = COALESCE(time_of_day, 'unknown'),
    day_of_week = COALESCE(day_of_week, 'unknown'),
    is_weekend = COALESCE(is_weekend, FALSE)
WHERE country IS NULL OR region IS NULL OR city IS NULL; 