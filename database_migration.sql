-- PayTosha Database Migration: Add Cascading Delete
-- Run this in your Supabase SQL Editor

-- Step 1: Drop existing foreign key constraint if it exists
-- (This will fail if the constraint doesn't exist, which is fine)
DO $$ 
BEGIN
    ALTER TABLE context_profiles DROP CONSTRAINT IF EXISTS context_profiles_user_id_fkey;
EXCEPTION
    WHEN undefined_object THEN
        -- Constraint doesn't exist, continue
        NULL;
END $$;

-- Step 2: Add foreign key constraint with CASCADE DELETE
ALTER TABLE context_profiles 
ADD CONSTRAINT context_profiles_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE CASCADE;

-- Step 3: Verify the constraint was created
-- You can check this in Supabase dashboard under Table Editor > context_profiles > Foreign Keys
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
    JOIN information_schema.referential_constraints AS rc
      ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name='context_profiles'
  AND kcu.column_name='user_id'; 