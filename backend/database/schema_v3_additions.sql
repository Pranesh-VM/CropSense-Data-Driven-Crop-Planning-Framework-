-- ============================================================================
-- SEED TRAINING DATA FOR LSTM MODEL
-- ============================================================================
-- This file creates synthetic historical data for LSTM training.
-- Run this AFTER schema_v2.sql and schema_v3_additions.sql
-- 
-- Usage in pgAdmin:
--   1. Open Query Tool on cropsense_db
--   2. Open this file or paste contents
--   3. Execute (F5)
-- ============================================================================

-- ============================================================================
-- 1. CREATE SAMPLE FARMERS (for LSTM training - won't conflict with real users)
-- ============================================================================
INSERT INTO farmers (farmer_id, username, email, password_hash, phone, is_active) 
VALUES 
    (1001, 'lstm_train_farmer_a', 'lstm_a@cropsense.ai', '$2b$12$seedhash123456789abcdefghijklmnop', '9000000001', TRUE),
    (1002, 'lstm_train_farmer_b', 'lstm_b@cropsense.ai', '$2b$12$seedhash123456789abcdefghijklmnop', '9000000002', TRUE),
    (1003, 'lstm_train_farmer_c', 'lstm_c@cropsense.ai', '$2b$12$seedhash123456789abcdefghijklmnop', '9000000003', TRUE)
ON CONFLICT (farmer_id) DO NOTHING;

-- ============================================================================
-- 2. CREATE FIELDS FOR EACH FARMER (different soil types)
-- ============================================================================
INSERT INTO fields (field_id, farmer_id, field_name, area_hectares, soil_type, soil_ph, latitude, longitude)
VALUES
    -- Farmer A: Loamy soil fields (Central India)
    (2001, 1001, 'Field A1 - Loamy', 5.0, 'loamy', 6.5, 23.2599, 77.4126),
    (2002, 1001, 'Field A2 - Loamy', 3.5, 'loamy', 6.8, 23.2610, 77.4150),
    
    -- Farmer B: Clay soil fields (South India)
    (2003, 1002, 'Field B1 - Clay', 4.0, 'clay', 7.0, 13.0827, 80.2707),
    (2004, 1002, 'Field B2 - Clay', 6.0, 'clay', 6.9, 13.0840, 80.2720),
    (2005, 1002, 'Field B3 - Clay', 2.5, 'clay', 7.2, 13.0850, 80.2730),
    
    -- Farmer C: Sandy soil fields (West India - Rajasthan)
    (2006, 1003, 'Field C1 - Sandy', 8.0, 'sandy', 7.5, 26.9124, 75.7873),
    (2007, 1003, 'Field C2 - Sandy', 4.5, 'sandy', 7.8, 26.9140, 75.7890),
    (2008, 1003, 'Field C3 - Sandy', 3.0, 'sandy', 7.3, 26.9150, 75.7900)
ON CONFLICT (field_id) DO NOTHING;

-- ============================================================================
-- 3. INSERT CROP NUTRIENT REQUIREMENTS (if not exists)
-- ============================================================================
INSERT INTO crop_nutrient_requirements (crop_name, n_uptake_kg_ha, p_uptake_kg_ha, k_uptake_kg_ha, cycle_days, average_yield_tonnes_ha)
VALUES
    ('rice', 80, 35, 80, 120, 4.5),
    ('wheat', 60, 25, 40, 140, 3.5),
    ('maize', 90, 40, 70, 100, 5.0),
    ('cotton', 70, 30, 60, 180, 2.0),
    ('sugarcane', 150, 50, 200, 365, 70.0),
    ('soybean', 20, 20, 40, 100, 2.5),
    ('groundnut', 25, 30, 45, 120, 2.0),
    ('chickpea', 15, 25, 30, 110, 1.5),
    ('lentil', 15, 20, 25, 100, 1.2),
    ('mungbean', 20, 15, 30, 70, 1.0),
    ('jute', 50, 20, 60, 150, 2.5),
    ('coffee', 100, 20, 120, 365, 1.5)
ON CONFLICT (crop_name) DO NOTHING;

-- ============================================================================
-- 4. CREATE COMPLETED CROP CYCLES (historical data for training)
-- ============================================================================
INSERT INTO crop_cycles (
    cycle_id, farmer_id, field_id, cycle_number, crop_name, 
    start_date, expected_end_date, actual_end_date, status,
    initial_n_kg_ha, initial_p_kg_ha, initial_k_kg_ha, initial_ph,
    current_n_kg_ha, current_p_kg_ha, current_k_kg_ha,
    final_n_kg_ha, final_p_kg_ha, final_k_kg_ha,
    total_crop_uptake_n, total_crop_uptake_p, total_crop_uptake_k,
    total_rainfall_loss_n, total_rainfall_loss_p, total_rainfall_loss_k,
    soil_type, soil_ph, rainfall_event_count, actual_yield_tonnes_ha
)
VALUES
    -- Farmer A: Rice cycles (Kharif season - Jun to Oct)
    (5001, 1001, 2001, 1, 'rice', 
     '2024-06-15', '2024-10-15', '2024-10-12', 'completed',
     90, 45, 55, 6.5,
     42, 28, 32,
     42, 28, 32,
     35, 12, 18,
     13, 5, 5,
     'loamy', 6.5, 15, 4.2),
    
    -- Farmer A: Wheat cycle (Rabi season - Nov to Mar)
    (5002, 1001, 2001, 2, 'wheat',
     '2024-11-01', '2025-03-15', '2025-03-10', 'completed',
     42, 28, 32, 6.5,
     18, 15, 20,
     18, 15, 20,
     22, 11, 10,
     2, 2, 2,
     'loamy', 6.5, 3, 3.8),
    
    -- Farmer A: Maize cycle (Zaid season - Mar to Jun)
    (5003, 1001, 2002, 1, 'maize',
     '2024-03-01', '2024-06-10', '2024-06-08', 'completed',
     85, 50, 60, 6.8,
     35, 25, 30,
     35, 25, 30,
     42, 20, 25,
     8, 5, 5,
     'loamy', 6.8, 8, 5.2),
    
    -- Farmer B: Rice on clay (slower drainage, less leaching)
    (5004, 1002, 2003, 1, 'rice',
     '2024-06-20', '2024-10-20', '2024-10-18', 'completed',
     95, 48, 58, 7.0,
     52, 32, 38,
     52, 32, 38,
     35, 12, 15,
     8, 4, 5,
     'clay', 7.0, 18, 4.8),
    
    -- Farmer B: Cotton on clay
    (5005, 1002, 2004, 1, 'cotton',
     '2024-04-01', '2024-10-01', '2024-09-28', 'completed',
     88, 42, 52, 6.9,
     30, 18, 22,
     30, 18, 22,
     50, 20, 25,
     8, 4, 5,
     'clay', 6.9, 12, 2.1),
    
    -- Farmer B: Chickpea (legume - nitrogen fixer)
    (5006, 1002, 2005, 1, 'chickpea',
     '2024-10-15', '2025-02-01', '2025-01-28', 'completed',
     40, 35, 45, 7.2,
     55, 22, 32,
     55, 22, 32,
     -20, 10, 10,
     5, 3, 3,
     'clay', 7.2, 4, 1.6),
    
    -- Farmer C: Groundnut on sandy (high leaching)
    (5007, 1003, 2006, 1, 'groundnut',
     '2024-06-15', '2024-10-15', '2024-10-10', 'completed',
     75, 40, 50, 7.5,
     25, 15, 20,
     25, 15, 20,
     30, 15, 20,
     20, 10, 10,
     'sandy', 7.5, 10, 1.8),
    
    -- Farmer C: Wheat on sandy
    (5008, 1003, 2007, 1, 'wheat',
     '2024-11-01', '2025-03-15', '2025-03-12', 'completed',
     70, 38, 48, 7.8,
     28, 20, 28,
     28, 20, 28,
     35, 15, 15,
     7, 3, 5,
     'sandy', 7.8, 5, 3.2),
    
    -- Farmer C: Mungbean (short duration legume)
    (5009, 1003, 2008, 1, 'mungbean',
     '2025-03-15', '2025-05-25', '2025-05-22', 'completed',
     50, 30, 40, 7.3,
     60, 20, 28,
     60, 20, 28,
     -15, 8, 10,
     5, 2, 2,
     'sandy', 7.3, 3, 1.1),
    
    -- Farmer A: Second rice cycle (showing rotation benefit)
    (5010, 1001, 2001, 3, 'rice',
     '2025-06-15', '2025-10-15', '2025-10-10', 'completed',
     55, 30, 40, 6.5,
     25, 18, 22,
     25, 18, 22,
     25, 10, 15,
     5, 2, 3,
     'loamy', 6.5, 12, 4.0)
ON CONFLICT (cycle_id) DO NOTHING;

-- ============================================================================
-- 5. GENERATE DAILY NUTRIENT TIMESERIES (LSTM Training Data)
-- ============================================================================
-- This generates ~120 days of daily data per cycle (1200+ rows total)

-- Function to generate timeseries for a single cycle
DO $$
DECLARE
    cycle_rec RECORD;
    day_offset INTEGER;
    current_n DECIMAL(8,2);
    current_p DECIMAL(8,2);
    current_k DECIMAL(8,2);
    daily_rainfall DECIMAL(8,2);
    daily_temp DECIMAL(5,2);
    daily_humidity DECIMAL(5,2);
    soil_coeff DECIMAL(4,2);
    crop_n_daily DECIMAL(6,4);
    crop_p_daily DECIMAL(6,4);
    crop_k_daily DECIMAL(6,4);
    cycle_duration INTEGER;
BEGIN
    -- Process each completed cycle
    FOR cycle_rec IN 
        SELECT * FROM crop_cycles WHERE status = 'completed' AND cycle_id >= 5001
    LOOP
        -- Set initial values
        current_n := cycle_rec.initial_n_kg_ha;
        current_p := cycle_rec.initial_p_kg_ha;
        current_k := cycle_rec.initial_k_kg_ha;
        
        -- Calculate cycle duration
        cycle_duration := cycle_rec.actual_end_date - cycle_rec.start_date;
        IF cycle_duration IS NULL OR cycle_duration <= 0 THEN
            cycle_duration := 120;
        END IF;
        
        -- Soil coefficient (affects leaching rate)
        CASE cycle_rec.soil_type
            WHEN 'sandy' THEN soil_coeff := 0.12;
            WHEN 'loamy' THEN soil_coeff := 0.08;
            WHEN 'clay' THEN soil_coeff := 0.05;
            ELSE soil_coeff := 0.08;
        END CASE;
        
        -- Daily crop uptake (total uptake / duration)
        crop_n_daily := COALESCE(cycle_rec.total_crop_uptake_n, 30) / cycle_duration;
        crop_p_daily := COALESCE(cycle_rec.total_crop_uptake_p, 12) / cycle_duration;
        crop_k_daily := COALESCE(cycle_rec.total_crop_uptake_k, 15) / cycle_duration;
        
        -- Generate daily records
        FOR day_offset IN 0..cycle_duration LOOP
            -- Simulate rainfall (seasonal pattern + randomness)
            -- Kharif (Jun-Oct): High rainfall
            -- Rabi (Nov-Mar): Low rainfall
            IF EXTRACT(MONTH FROM (cycle_rec.start_date + day_offset)) BETWEEN 6 AND 10 THEN
                daily_rainfall := GREATEST(0, 8 + (random() * 25) - 10);
            ELSE
                daily_rainfall := GREATEST(0, 2 + (random() * 8) - 5);
            END IF;
            
            -- Simulate temperature (seasonal)
            daily_temp := 25 + (random() * 10) - 5 + 
                CASE 
                    WHEN EXTRACT(MONTH FROM (cycle_rec.start_date + day_offset)) BETWEEN 4 AND 6 THEN 5
                    WHEN EXTRACT(MONTH FROM (cycle_rec.start_date + day_offset)) BETWEEN 11 AND 2 THEN -5
                    ELSE 0
                END;
            
            -- Simulate humidity
            daily_humidity := 60 + (random() * 30) + 
                CASE WHEN daily_rainfall > 5 THEN 15 ELSE 0 END;
            daily_humidity := LEAST(95, daily_humidity);
            
            -- Apply nutrient depletion
            -- Rainfall leaching loss
            current_n := current_n - (daily_rainfall * soil_coeff * 0.7);
            current_p := current_p - (daily_rainfall * soil_coeff * 0.3);
            current_k := current_k - (daily_rainfall * soil_coeff * 0.5);
            
            -- Crop uptake
            current_n := current_n - crop_n_daily;
            current_p := current_p - crop_p_daily;
            current_k := current_k - crop_k_daily;
            
            -- Ensure non-negative
            current_n := GREATEST(5, current_n);
            current_p := GREATEST(3, current_p);
            current_k := GREATEST(5, current_k);
            
            -- Insert timeseries record
            INSERT INTO nutrient_timeseries_log (
                cycle_id, farmer_id, log_date,
                n_kg_ha, p_kg_ha, k_kg_ha,
                rainfall_mm, temperature_avg, humidity_avg,
                days_into_cycle
            ) VALUES (
                cycle_rec.cycle_id,
                cycle_rec.farmer_id,
                cycle_rec.start_date + day_offset,
                ROUND(current_n::numeric, 2),
                ROUND(current_p::numeric, 2),
                ROUND(current_k::numeric, 2),
                ROUND(daily_rainfall::numeric, 2),
                ROUND(daily_temp::numeric, 2),
                ROUND(daily_humidity::numeric, 2),
                day_offset
            ) ON CONFLICT (cycle_id, log_date) DO NOTHING;
            
        END LOOP;
    END LOOP;
END $$;

-- ============================================================================
-- 6. POPULATE CYCLE PERFORMANCE HISTORY (Q-Learning Rewards)
-- ============================================================================
INSERT INTO cycle_performance_history (
    farmer_id, field_id, cycle_id, crop_name, season,
    start_date, end_date, duration_days,
    initial_n, initial_p, initial_k,
    final_n, final_p, final_k,
    total_rainfall_mm, yield_kg_ha, market_price_per_kg,
    profit_per_ha, soil_penalty, reward
)
SELECT 
    cc.farmer_id,
    cc.field_id,
    cc.cycle_id,
    cc.crop_name,
    CASE 
        WHEN EXTRACT(MONTH FROM cc.start_date) BETWEEN 6 AND 10 THEN 'kharif'
        WHEN EXTRACT(MONTH FROM cc.start_date) BETWEEN 11 AND 12 OR EXTRACT(MONTH FROM cc.start_date) BETWEEN 1 AND 2 THEN 'rabi'
        WHEN EXTRACT(MONTH FROM cc.start_date) BETWEEN 3 AND 5 THEN 'zaid'
        ELSE 'annual'
    END as season,
    cc.start_date,
    cc.actual_end_date,
    cc.actual_end_date - cc.start_date as duration_days,
    cc.initial_n_kg_ha,
    cc.initial_p_kg_ha,
    cc.initial_k_kg_ha,
    cc.final_n_kg_ha,
    cc.final_p_kg_ha,
    cc.final_k_kg_ha,
    COALESCE(cc.total_rainfall_loss_n / 0.056, 200) as total_rainfall_mm,
    cc.actual_yield_tonnes_ha * 1000 as yield_kg_ha,
    CASE cc.crop_name
        WHEN 'rice' THEN 22.0
        WHEN 'wheat' THEN 25.0
        WHEN 'maize' THEN 18.0
        WHEN 'cotton' THEN 55.0
        WHEN 'chickpea' THEN 60.0
        WHEN 'groundnut' THEN 50.0
        WHEN 'mungbean' THEN 70.0
        ELSE 20.0
    END as market_price_per_kg,
    -- profit = yield * price
    cc.actual_yield_tonnes_ha * 1000 * 
        CASE cc.crop_name
            WHEN 'rice' THEN 22.0
            WHEN 'wheat' THEN 25.0
            WHEN 'maize' THEN 18.0
            WHEN 'cotton' THEN 55.0
            WHEN 'chickpea' THEN 60.0
            WHEN 'groundnut' THEN 50.0
            WHEN 'mungbean' THEN 70.0
            ELSE 20.0
        END as profit_per_ha,
    -- soil penalty = (initial - final) * 100
    ((cc.initial_n_kg_ha - COALESCE(cc.final_n_kg_ha, cc.current_n_kg_ha)) +
     (cc.initial_p_kg_ha - COALESCE(cc.final_p_kg_ha, cc.current_p_kg_ha)) +
     (cc.initial_k_kg_ha - COALESCE(cc.final_k_kg_ha, cc.current_k_kg_ha))) * 100 as soil_penalty,
    -- reward = profit - penalty
    cc.actual_yield_tonnes_ha * 1000 * 
        CASE cc.crop_name
            WHEN 'rice' THEN 22.0
            WHEN 'wheat' THEN 25.0
            WHEN 'maize' THEN 18.0
            WHEN 'cotton' THEN 55.0
            WHEN 'chickpea' THEN 60.0
            WHEN 'groundnut' THEN 50.0
            WHEN 'mungbean' THEN 70.0
            ELSE 20.0
        END -
    ((cc.initial_n_kg_ha - COALESCE(cc.final_n_kg_ha, cc.current_n_kg_ha)) +
     (cc.initial_p_kg_ha - COALESCE(cc.final_p_kg_ha, cc.current_p_kg_ha)) +
     (cc.initial_k_kg_ha - COALESCE(cc.final_k_kg_ha, cc.current_k_kg_ha))) * 100 as reward
FROM crop_cycles cc
WHERE cc.status = 'completed' AND cc.cycle_id >= 5001
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 7. POPULATE MARKET PRICES (Historical - for future Prophet training)
-- ============================================================================
DO $$
DECLARE
    crop_name_var VARCHAR(50);
    base_price DECIMAL(8,2);
    p_date DATE;
    seasonal_factor DECIMAL(4,2);
BEGIN
    -- Generate 365 days of price history for each major crop
    FOREACH crop_name_var IN ARRAY ARRAY['rice', 'wheat', 'maize', 'cotton', 'chickpea', 'groundnut', 'mungbean']
    LOOP
        -- Base price per crop
        CASE crop_name_var
            WHEN 'rice' THEN base_price := 22.0;
            WHEN 'wheat' THEN base_price := 25.0;
            WHEN 'maize' THEN base_price := 18.0;
            WHEN 'cotton' THEN base_price := 55.0;
            WHEN 'chickpea' THEN base_price := 60.0;
            WHEN 'groundnut' THEN base_price := 50.0;
            WHEN 'mungbean' THEN base_price := 70.0;
            ELSE base_price := 20.0;
        END CASE;
        
        -- Generate daily prices for past year
        FOR day_offset IN 0..364 LOOP
            p_date := CURRENT_DATE - day_offset;
            
            -- Seasonal price variation (+/- 15%)
            seasonal_factor := 1.0 + 0.15 * SIN(2 * 3.14159 * day_offset / 365);
            
            INSERT INTO market_prices (crop_name, price_date, price_per_kg, market_name, state_name)
            VALUES (
                crop_name_var,
                p_date,
                ROUND((base_price * seasonal_factor + (random() * 4 - 2))::numeric, 2),
                'APMC Mandi',
                'Maharashtra'
            ) ON CONFLICT (crop_name, price_date, market_name) DO NOTHING;
        END LOOP;
    END LOOP;
END $$;

-- ============================================================================
-- 8. VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify data was inserted correctly:

SELECT 'farmers' as table_name, COUNT(*) as record_count FROM farmers WHERE farmer_id >= 1001
UNION ALL
SELECT 'fields', COUNT(*) FROM fields WHERE field_id >= 2001
UNION ALL
SELECT 'crop_cycles', COUNT(*) FROM crop_cycles WHERE cycle_id >= 5001
UNION ALL
SELECT 'nutrient_timeseries_log', COUNT(*) FROM nutrient_timeseries_log
UNION ALL
SELECT 'cycle_performance_history', COUNT(*) FROM cycle_performance_history
UNION ALL
SELECT 'market_prices', COUNT(*) FROM market_prices;

-- Sample timeseries data (first 10 rows)
-- SELECT * FROM nutrient_timeseries_log WHERE cycle_id = 5001 ORDER BY log_date LIMIT 10;

-- ============================================================================
-- DONE! LSTM training data is now ready.
-- Expected counts:
--   farmers: 3
--   fields: 8
--   crop_cycles: 10
--   nutrient_timeseries_log: ~1200 rows
--   cycle_performance_history: 10
--   market_prices: ~2555 rows (7 crops × 365 days)
-- ============================================================================