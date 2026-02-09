-- ============================================================================
-- CropSense Database Setup - Direct psql Commands
-- ============================================================================
-- Run these commands in pgAdmin or psql to set up the database from scratch

-- Step 1: Drop existing database (if it exists)
DROP DATABASE IF EXISTS cropsense_db;

-- Step 2: Create new database
CREATE DATABASE cropsense_db;

-- Step 3: Connect to the new database and import schema
-- Option A: If using psql command line:
--   psql -U postgres -d cropsense_db -f schema_v2.sql
--
-- Option B: If using pgAdmin:
--   1. Right-click "Databases" → Create → Database
--   2. Name: cropsense_db
--   3. Create
--   4. Right-click cropsense_db → Restore
--   5. Select schema_v2.sql
--
-- Option C: Copy-paste the entire schema_v2.sql content into Query Editor

-- ============================================================================
-- ALTERNATIVE: Direct SQL (if you want to run everything in one go)
-- ============================================================================
-- Uncomment and use the schema below, or better yet, use schema_v2.sql

-- \c cropsense_db

-- DROP TABLE IF EXISTS rainfall_events CASCADE;
-- DROP TABLE IF EXISTS nutrient_measurements CASCADE;
-- DROP TABLE IF EXISTS crop_cycles CASCADE;
-- DROP TABLE IF EXISTS fields CASCADE;
-- DROP TABLE IF EXISTS farmers CASCADE;
-- DROP TABLE IF EXISTS crop_nutrient_requirements CASCADE;
-- DROP TABLE IF EXISTS soil_test_recommendations CASCADE;
-- DROP TABLE IF EXISTS cycle_recommendations CASCADE;

-- [Full schema content would go here - see schema_v2.sql]
