-- Fix Orphaned Context Profiles
-- Run this BEFORE the main migration to clean up any orphaned records

-- Step 1: Find orphaned context profiles (context_profiles with user_id that don't exist in users table)
SELECT 
    cp.id,
    cp.user_id,
    cp.username,
    cp.created_at
FROM context_profiles cp
LEFT JOIN users u ON cp.user_id = u.id
WHERE u.id IS NULL;

-- Step 2: Delete orphaned context profiles
DELETE FROM context_profiles 
WHERE user_id NOT IN (SELECT id FROM users);

-- Step 3: Verify no orphaned records remain
SELECT 
    COUNT(*) as orphaned_count
FROM context_profiles cp
LEFT JOIN users u ON cp.user_id = u.id
WHERE u.id IS NULL;

-- Step 4: Now you can safely run the main migration
-- (Go back to database_migration.sql and run it) 