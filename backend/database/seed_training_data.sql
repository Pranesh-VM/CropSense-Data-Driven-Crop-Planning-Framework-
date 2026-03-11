-- ============================================================================
-- SEED TRAINING DATA FOR LSTM MODEL
-- ============================================================================
-- This file creates synthetic historical data for LSTM training.
-- Run this AFTER schema_v2.sql and schema_v3_additions.sql
-- 
-- The data simulates realistic crop cycles with:
-- - Multiple soil types (loamy, clay, sandy)
-- - Various crops (rice, wheat, maize)
-- - Seasonal rainfall patterns
-- - Nutrient depletion over time
-- ============================================================================

-- ============================================================================
-- 1. CREATE SAMPLE FARMERS (if not exists)
-- ============================================================================
INSERT INTO farmers (farmer_id, name, email, password, region, farm_size_hectares) 
VALUES 
    (1001, 'LSTM_Train_A', 'lstm_a@cropsense.ai', '$2b$12$seedhash123456789abcde', 'Central Region', 25.0),
    (1002, 'LSTM_Train_B', 'lstm_b@cropsense.ai', '$2b$12$seedhash123456789abcde', 'North Region', 18.5),
    (1003, 'LSTM_Train_C', 'lstm_c@cropsense.ai', '$2b$12$seedhash123456789abcde', 'East Region', 30.0)
ON CONFLICT (farmer_id) DO NOTHING;

-- ============================================================================
-- 2. CREATE SAMPLE FIELDS (different soil types)
-- ============================================================================
INSERT INTO fields (field_id, farmer_id, field_name, area_hectares, soil_type, slope_percent) 
VALUES 
    -- Farmer A fields
    (2001, 1001, 'North Field - Loamy', 8.0, 'loamy', 3.5),
    (2002, 1001, 'South Field - Clay', 10.0, 'clay', 2.0),
    (2003, 1001, 'East Field - Sandy', 7.0, 'sandy', 5.0),
    -- Farmer B fields
    (2004, 1002, 'Main Field - Loamy', 12.0, 'loamy', 2.5),
    (2005, 1002, 'River Field - Clay', 6.5, 'clay', 1.5),
    -- Farmer C fields
    (2006, 1003, 'Valley Field - Loamy', 15.0, 'loamy', 4.0),
    (2007, 1003, 'Hill Field - Sandy', 10.0, 'sandy', 6.5),
    (2008, 1003, 'Irrigated Field - Clay', 5.0, 'clay', 1.0)
ON CONFLICT (field_id) DO NOTHING;

-- ============================================================================
-- 3. CREATE HISTORICAL CROP CYCLES (completed)
-- ============================================================================
INSERT INTO crop_cycles (
    cycle_id, farmer_id, field_id, crop_name, 
    cycle_start_date, cycle_end_date, is_current,
    initial_n_kg_ha, initial_p_kg_ha, initial_k_kg_ha,
    final_n_kg_ha, final_p_kg_ha, final_k_kg_ha
) VALUES 
    -- Rice cycles (120 days) - High N consumer
    (5001, 1001, 2001, 'rice', '2023-06-01', '2023-09-28', false, 85.0, 45.0, 55.0, 28.5, 18.2, 22.1),
    (5002, 1002, 2004, 'rice', '2023-06-15', '2023-10-12', false, 90.0, 48.0, 52.0, 32.1, 21.5, 24.3),
    (5003, 1003, 2006, 'rice', '2023-07-01', '2023-10-28', false, 82.0, 42.0, 58.0, 25.8, 16.9, 26.5),
    
    -- Wheat cycles (135 days) - Moderate NPK consumer
    (5004, 1001, 2002, 'wheat', '2023-10-15', '2024-02-27', false, 75.0, 55.0, 48.0, 35.2, 28.4, 23.1),
    (5005, 1002, 2005, 'wheat', '2023-11-01', '2024-03-15', false, 78.0, 52.0, 50.0, 38.5, 26.2, 25.4),
    (5006, 1003, 2008, 'wheat', '2023-10-20', '2024-03-03', false, 72.0, 58.0, 45.0, 33.8, 30.5, 21.8),
    
    -- Maize cycles (100 days) - Balanced NPK
    (5007, 1001, 2003, 'maize', '2023-03-01', '2023-06-08', false, 70.0, 40.0, 60.0, 24.5, 15.8, 28.2),
    (5008, 1003, 2007, 'maize', '2023-03-15', '2023-06-22', false, 68.0, 38.0, 58.0, 22.1, 14.2, 25.6),
    
    -- More recent cycles (2024)
    (5009, 1001, 2001, 'rice', '2024-06-01', '2024-09-28', false, 88.0, 46.0, 54.0, 30.2, 19.5, 23.8),
    (5010, 1002, 2004, 'maize', '2024-04-01', '2024-07-09', false, 72.0, 42.0, 62.0, 26.8, 17.2, 30.5)
ON CONFLICT (cycle_id) DO NOTHING;

-- ============================================================================
-- 4. POPULATE NUTRIENT TIMESERIES (for LSTM training)
-- ============================================================================
-- This generates daily nutrient readings for each cycle

-- ===================== CYCLE 5001: Rice - Loamy =====================
-- Initial: N=85, P=45, K=55  |  Final: N=28.5, P=18.2, K=22.1 (120 days)
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2001 as field_id,
    5001 as cycle_id,
    '2023-06-01'::DATE + (n || ' days')::INTERVAL as log_date,
    -- N depletion: 85 -> 28.5 with daily decay + random noise
    GREATEST(28.5, 85.0 - (56.5 * n / 120.0) + (RANDOM() * 3 - 1.5)) as nitrogen_kg_ha,
    -- P depletion: 45 -> 18.2
    GREATEST(18.2, 45.0 - (26.8 * n / 120.0) + (RANDOM() * 2 - 1.0)) as phosphorus_kg_ha,
    -- K depletion: 55 -> 22.1
    GREATEST(22.1, 55.0 - (32.9 * n / 120.0) + (RANDOM() * 2.5 - 1.25)) as potassium_kg_ha
FROM generate_series(0, 119) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5002: Rice - Loamy =====================
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2004 as field_id,
    5002 as cycle_id,
    '2023-06-15'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(32.1, 90.0 - (57.9 * n / 119.0) + (RANDOM() * 3.2 - 1.6)) as nitrogen_kg_ha,
    GREATEST(21.5, 48.0 - (26.5 * n / 119.0) + (RANDOM() * 2 - 1.0)) as phosphorus_kg_ha,
    GREATEST(24.3, 52.0 - (27.7 * n / 119.0) + (RANDOM() * 2.2 - 1.1)) as potassium_kg_ha
FROM generate_series(0, 119) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5003: Rice - Loamy =====================
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2006 as field_id,
    5003 as cycle_id,
    '2023-07-01'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(25.8, 82.0 - (56.2 * n / 119.0) + (RANDOM() * 2.8 - 1.4)) as nitrogen_kg_ha,
    GREATEST(16.9, 42.0 - (25.1 * n / 119.0) + (RANDOM() * 1.8 - 0.9)) as phosphorus_kg_ha,
    GREATEST(26.5, 58.0 - (31.5 * n / 119.0) + (RANDOM() * 2.4 - 1.2)) as potassium_kg_ha
FROM generate_series(0, 119) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5004: Wheat - Clay =====================
-- Initial: N=75, P=55, K=48  |  Final: N=35.2, P=28.4, K=23.1 (135 days)
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2002 as field_id,
    5004 as cycle_id,
    '2023-10-15'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(35.2, 75.0 - (39.8 * n / 135.0) + (RANDOM() * 2.5 - 1.25)) as nitrogen_kg_ha,
    GREATEST(28.4, 55.0 - (26.6 * n / 135.0) + (RANDOM() * 2 - 1.0)) as phosphorus_kg_ha,
    GREATEST(23.1, 48.0 - (24.9 * n / 135.0) + (RANDOM() * 2.2 - 1.1)) as potassium_kg_ha
FROM generate_series(0, 134) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5005: Wheat - Clay =====================
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2005 as field_id,
    5005 as cycle_id,
    '2023-11-01'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(38.5, 78.0 - (39.5 * n / 135.0) + (RANDOM() * 2.6 - 1.3)) as nitrogen_kg_ha,
    GREATEST(26.2, 52.0 - (25.8 * n / 135.0) + (RANDOM() * 1.9 - 0.95)) as phosphorus_kg_ha,
    GREATEST(25.4, 50.0 - (24.6 * n / 135.0) + (RANDOM() * 2.1 - 1.05)) as potassium_kg_ha
FROM generate_series(0, 134) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5006: Wheat - Clay =====================
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2008 as field_id,
    5006 as cycle_id,
    '2023-10-20'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(33.8, 72.0 - (38.2 * n / 134.0) + (RANDOM() * 2.4 - 1.2)) as nitrogen_kg_ha,
    GREATEST(30.5, 58.0 - (27.5 * n / 134.0) + (RANDOM() * 2.1 - 1.05)) as phosphorus_kg_ha,
    GREATEST(21.8, 45.0 - (23.2 * n / 134.0) + (RANDOM() * 1.8 - 0.9)) as potassium_kg_ha
FROM generate_series(0, 134) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5007: Maize - Sandy =====================
-- Initial: N=70, P=40, K=60  |  Final: N=24.5, P=15.8, K=28.2 (100 days)
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2003 as field_id,
    5007 as cycle_id,
    '2023-03-01'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(24.5, 70.0 - (45.5 * n / 99.0) + (RANDOM() * 3 - 1.5)) as nitrogen_kg_ha,
    GREATEST(15.8, 40.0 - (24.2 * n / 99.0) + (RANDOM() * 1.8 - 0.9)) as phosphorus_kg_ha,
    GREATEST(28.2, 60.0 - (31.8 * n / 99.0) + (RANDOM() * 2.5 - 1.25)) as potassium_kg_ha
FROM generate_series(0, 99) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5008: Maize - Sandy =====================
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2007 as field_id,
    5008 as cycle_id,
    '2023-03-15'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(22.1, 68.0 - (45.9 * n / 99.0) + (RANDOM() * 3.2 - 1.6)) as nitrogen_kg_ha,
    GREATEST(14.2, 38.0 - (23.8 * n / 99.0) + (RANDOM() * 1.7 - 0.85)) as phosphorus_kg_ha,
    GREATEST(25.6, 58.0 - (32.4 * n / 99.0) + (RANDOM() * 2.6 - 1.3)) as potassium_kg_ha
FROM generate_series(0, 99) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5009: Rice 2024 - Loamy =====================
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2001 as field_id,
    5009 as cycle_id,
    '2024-06-01'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(30.2, 88.0 - (57.8 * n / 119.0) + (RANDOM() * 3.1 - 1.55)) as nitrogen_kg_ha,
    GREATEST(19.5, 46.0 - (26.5 * n / 119.0) + (RANDOM() * 2 - 1.0)) as phosphorus_kg_ha,
    GREATEST(23.8, 54.0 - (30.2 * n / 119.0) + (RANDOM() * 2.3 - 1.15)) as potassium_kg_ha
FROM generate_series(0, 119) as n
ON CONFLICT DO NOTHING;

-- ===================== CYCLE 5010: Maize 2024 - Loamy =====================
INSERT INTO nutrient_timeseries_log (
    field_id, cycle_id, log_date,
    nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha
)
SELECT 
    2004 as field_id,
    5010 as cycle_id,
    '2024-04-01'::DATE + (n || ' days')::INTERVAL as log_date,
    GREATEST(26.8, 72.0 - (45.2 * n / 99.0) + (RANDOM() * 2.9 - 1.45)) as nitrogen_kg_ha,
    GREATEST(17.2, 42.0 - (24.8 * n / 99.0) + (RANDOM() * 1.9 - 0.95)) as phosphorus_kg_ha,
    GREATEST(30.5, 62.0 - (31.5 * n / 99.0) + (RANDOM() * 2.4 - 1.2)) as potassium_kg_ha
FROM generate_series(0, 99) as n
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 5. POPULATE CYCLE PERFORMANCE HISTORY (for Q-Learning)
-- ============================================================================
INSERT INTO cycle_performance_history (
    farmer_id, field_id, cycle_id, crop_name,
    initial_n, initial_p, initial_k,
    final_n, final_p, final_k,
    total_rainfall_mm
) VALUES
    (1001, 2001, 5001, 'rice',  85.0, 45.0, 55.0, 28.5, 18.2, 22.1, 485.0),
    (1002, 2004, 5002, 'rice',  90.0, 48.0, 52.0, 32.1, 21.5, 24.3, 510.0),
    (1003, 2006, 5003, 'rice',  82.0, 42.0, 58.0, 25.8, 16.9, 26.5, 420.0),
    (1001, 2002, 5004, 'wheat', 75.0, 55.0, 48.0, 35.2, 28.4, 23.1, 180.0),
    (1002, 2005, 5005, 'wheat', 78.0, 52.0, 50.0, 38.5, 26.2, 25.4, 165.0),
    (1003, 2008, 5006, 'wheat', 72.0, 58.0, 45.0, 33.8, 30.5, 21.8, 195.0),
    (1001, 2003, 5007, 'maize', 70.0, 40.0, 60.0, 24.5, 15.8, 28.2, 320.0),
    (1003, 2007, 5008, 'maize', 68.0, 38.0, 58.0, 22.1, 14.2, 25.6, 285.0),
    (1001, 2001, 5009, 'rice',  88.0, 46.0, 54.0, 30.2, 19.5, 23.8, 540.0),
    (1002, 2004, 5010, 'maize', 72.0, 42.0, 62.0, 26.8, 17.2, 30.5, 295.0)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 6. SUMMARY
-- ============================================================================
-- After running this script:
-- - 3 sample farmers created (farmer_id 1001-1003)
-- - 8 fields with different soil types created
-- - 10 completed crop cycles with nutrient data
-- - ~1150 nutrient timeseries records (daily readings)
-- - 10 cycle performance history records
--
-- This provides sufficient data for initial LSTM training.
-- ============================================================================

-- Verify data counts
SELECT 'farmers' as table_name, COUNT(*) as record_count FROM farmers WHERE farmer_id >= 1001 AND farmer_id <= 1003
UNION ALL
SELECT 'fields', COUNT(*) FROM fields WHERE field_id >= 2001 AND field_id <= 2008
UNION ALL
SELECT 'crop_cycles', COUNT(*) FROM crop_cycles WHERE cycle_id >= 5001 AND cycle_id <= 5010
UNION ALL
SELECT 'nutrient_timeseries_log', COUNT(*) FROM nutrient_timeseries_log WHERE cycle_id >= 5001 AND cycle_id <= 5010
UNION ALL
SELECT 'cycle_performance_history', COUNT(*) FROM cycle_performance_history WHERE cycle_id >= 5001 AND cycle_id <= 5010;
