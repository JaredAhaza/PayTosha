-- Add separate social media columns to context_profiles table
-- Run this in your Supabase SQL Editor

-- Add new social media columns
ALTER TABLE context_profiles 
ADD COLUMN IF NOT EXISTS twitter_data JSONB DEFAULT NULL;

ALTER TABLE context_profiles 
ADD COLUMN IF NOT EXISTS facebook_data JSONB DEFAULT NULL;

ALTER TABLE context_profiles 
ADD COLUMN IF NOT EXISTS github_data JSONB DEFAULT NULL;

ALTER TABLE context_profiles 
ADD COLUMN IF NOT EXISTS personal_website_data JSONB DEFAULT NULL;

-- Verify the columns were added
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'context_profiles' 
  AND column_name IN ('linkedin_data', 'twitter_data', 'facebook_data', 'github_data', 'personal_website_data')
ORDER BY column_name; 