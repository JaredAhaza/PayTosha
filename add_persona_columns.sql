-- Add new persona-related columns to context_profiles table
-- Run this in your Supabase SQL Editor

-- Add persona_confidence column
ALTER TABLE context_profiles 
ADD COLUMN IF NOT EXISTS persona_confidence TEXT DEFAULT 'low';

-- Add persona_sources column (array of text)
ALTER TABLE context_profiles 
ADD COLUMN IF NOT EXISTS persona_sources TEXT[] DEFAULT '{}';

-- Add persona_reasoning column (array of text)
ALTER TABLE context_profiles 
ADD COLUMN IF NOT EXISTS persona_reasoning TEXT[] DEFAULT '{}';

-- Verify the columns were added
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'context_profiles' 
  AND column_name IN ('persona_confidence', 'persona_sources', 'persona_reasoning')
ORDER BY column_name; 