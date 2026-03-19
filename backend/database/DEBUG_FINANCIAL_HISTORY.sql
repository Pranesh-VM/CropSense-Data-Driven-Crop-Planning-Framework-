-- ============================================================================
-- DEBUG FINANCIAL HISTORY ISSUES
-- ============================================================================
-- Run these queries in order to diagnose why data isn't showing
-- Copy output and share if issues persist
-- ============================================================================

-- STEP 1: Check if cycle_performance_history table exists
SELECT table_name FROM information_schema.tables 
WHERE table_name = 'cycle_performance_history';

-- STEP 2: List all columns in the table
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'cycle_performance_history' 
ORDER BY ordinal_position;

-- STEP 3: Check current data in table
SELECT * FROM cycle_performance_history LIMIT 10;

-- STEP 4: Check data for farmer_id = 1
SELECT crop_name, farmer_id, profit_per_ha, start_date FROM cycle_performance_history 
WHERE farmer_id = 1;

-- STEP 5: Check all farmers in the system
SELECT DISTINCT farmer_id FROM cycle_performance_history;

-- STEP 6: Check farmers table
SELECT farmer_id, username, email FROM farmers LIMIT 5;

-- STEP 7: Check which farmer_id corresponds to logged-in user
-- (If you know your username/email, update this query)
SELECT farmer_id, username, email FROM farmers 
WHERE username = 'YOUR_USERNAME_HERE' OR email = 'YOUR_EMAIL_HERE';

-- STEP 8: If you found your farmer_id in STEP 7, use it here
-- Example: If farmer_id is 5, use WHERE farmer_id = 5
SELECT crop_name, profit_per_ha, start_date FROM cycle_performance_history 
WHERE farmer_id = 1  -- Change this to YOUR farmer_id if different
ORDER BY start_date DESC;

-- STEP 9: Compare with crop_cycles (what endpoint falls back to)
SELECT cc.cycle_id, cc.crop_name, cc.start_date, cc.actual_end_date 
FROM crop_cycles cc
LIMIT 5;

-- STEP 10: Re-insert data (if needed) with correct farmer_id
-- First, DELETE old test data
-- DELETE FROM cycle_performance_history 
-- WHERE farmer_id = 1 AND crop_name IN ('Rice Demo', 'Wheat Demo', 'Maize Demo');

-- Then re-run INSERT_FINANCIAL_HISTORY.sql

-- STEP 11: Verify after insert
-- SELECT COUNT(*) as inserted_rows FROM cycle_performance_history 
-- WHERE crop_name IN ('Rice Demo', 'Wheat Demo', 'Maize Demo');
