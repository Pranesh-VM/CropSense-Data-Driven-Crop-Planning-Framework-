-- ============================================================================
-- CropSense Database - Seed Data
-- Crop Nutrient Requirements for all 22 crops
-- ============================================================================
--
-- This file populates the crop_nutrient_requirements table with research-based
-- nutrient uptake data for all crops supported by the CropSense system.
--
-- Data sources:
-- - ICAR (Indian Council of Agricultural Research)
-- - FAO (Food & Agriculture Organization)
-- - USDA (United States Department of Agriculture)
-- - State Agricultural Universities
--
-- Units:
-- - Nutrient uptake: kg/ha (kilograms per hectare)
-- - Temperature: °C (Celsius)
-- - Water requirement: mm (millimeters)
-- - Yield: tonnes/ha
--
-- ============================================================================

-- Clear existing data (if re-importing)
TRUNCATE TABLE crop_nutrient_requirements CASCADE;

-- ============================================================================
-- Insert all 22 crops with nutrient requirements
-- ============================================================================

INSERT INTO crop_nutrient_requirements (
    crop_name,
    n_uptake_kg_ha,
    p_uptake_kg_ha,
    k_uptake_kg_ha,
    cycle_days,
    average_yield_tonnes_ha,
    optimal_temp_min_c,
    optimal_temp_max_c,
    water_requirement_mm,
    data_source
) VALUES

-- =========================
-- CEREALS
-- =========================

('rice', 120, 40, 140, 120, 5.0, 20, 30, 1000, 'ICAR Rice Research Institute 2020'),
('maize', 150, 50, 180, 100, 6.0, 21, 27, 400, 'FAO Maize Production Guide 2019'),

-- =========================
-- PULSES (LEGUMES)
-- =========================

('chickpea', 80, 30, 40, 100, 2.0, 15, 25, 250, 'ICAR Pulses Research Directorate'),
('kidneybeans', 70, 25, 50, 90, 1.8, 18, 28, 300, 'USDA Bean Production Handbook'),
('pigeonpeas', 75, 30, 45, 240, 2.2, 20, 30, 600, 'ICAR Pulses Research Directorate'),
('mothbeans', 60, 20, 35, 75, 1.5, 20, 30, 200, 'ICAR Arid Zone Research Institute'),
('mungbean', 65, 22, 40, 60, 1.2, 25, 30, 250, 'ICAR Pulses Research Directorate'),
('blackgram', 70, 25, 45, 90, 1.5, 20, 30, 300, 'ICAR Pulses Research Directorate'),
('lentil', 75, 28, 42, 110, 1.8, 15, 25, 200, 'FAO Lentil Production Guide'),

-- =========================
-- FRUITS (PERENNIAL)
-- =========================

('pomegranate', 200, 60, 250, 210, 15.0, 20, 30, 600, 'ICAR National Research Centre on Pomegranate'),
('banana', 300, 80, 500, 270, 40.0, 18, 28, 1500, 'ICAR National Research Centre for Banana'),
('mango', 250, 70, 300, 150, 10.0, 24, 30, 600, 'ICAR Central Institute for Subtropical Horticulture'),
('coconut', 180, 50, 350, 365, 8.0, 24, 32, 1500, 'ICAR Central Plantation Crops Research Institute'),
('apple', 180, 55, 220, 150, 12.0, 7, 24, 600, 'ICAR Central Institute for Temperate Horticulture'),
('orange', 200, 60, 240, 240, 20.0, 13, 29, 1000, 'ICAR Central Citrus Research Institute'),
('papaya', 150, 45, 200, 270, 30.0, 21, 32, 1000, 'ICAR Indian Institute of Horticultural Research'),
('watermelon', 100, 35, 150, 80, 25.0, 21, 32, 400, 'FAO Vegetable Production Handbook'),
('grapes', 140, 48, 190, 150, 18.0, 12, 28, 500, 'ICAR National Research Centre for Grapes'),
('muskmelon', 90, 30, 130, 90, 20.0, 21, 30, 400, 'FAO Vegetable Production Handbook'),

-- =========================
-- COMMERCIAL CROPS
-- =========================

('cotton', 160, 55, 200, 180, 3.0, 21, 30, 600, 'ICAR Central Institute for Cotton Research'),
('coffee', 220, 65, 280, 365, 1.5, 15, 24, 1500, 'Coffee Board of India Research'),
('jute', 110, 40, 90, 120, 2.5, 24, 30, 2000, 'ICAR Central Research Institute for Jute');


-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Total crops inserted
SELECT COUNT(*) AS total_crops FROM crop_nutrient_requirements;

-- Summary by category
SELECT 
    CASE 
        WHEN crop_name IN ('rice', 'maize') THEN 'Cereals'
        WHEN crop_name IN ('chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 'lentil') THEN 'Pulses'
        WHEN crop_name IN ('pomegranate', 'banana', 'mango', 'coconut', 'apple', 'orange', 'papaya', 'watermelon', 'grapes', 'muskmelon') THEN 'Fruits'
        ELSE 'Commercial'
    END AS category,
    COUNT(*) AS crop_count,
    ROUND(AVG(n_uptake_kg_ha), 2) AS avg_n,
    ROUND(AVG(p_uptake_kg_ha), 2) AS avg_p,
    ROUND(AVG(k_uptake_kg_ha), 2) AS avg_k
FROM crop_nutrient_requirements
GROUP BY category
ORDER BY category;

-- Crops sorted by total nutrient uptake
SELECT 
    crop_name,
    n_uptake_kg_ha AS N,
    p_uptake_kg_ha AS P,
    k_uptake_kg_ha AS K,
    (n_uptake_kg_ha + p_uptake_kg_ha + k_uptake_kg_ha) AS total_uptake,
    cycle_days
FROM crop_nutrient_requirements
ORDER BY total_uptake DESC
LIMIT 10;

-- ============================================================================
-- Seed Data Import Complete
-- ============================================================================

-- Output confirmation
DO $$
DECLARE
    crop_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO crop_count FROM crop_nutrient_requirements;
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Crop Nutrient Data Import Complete!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Total crops imported: %', crop_count;
    RAISE NOTICE 'Database: cropsense_db';
    RAISE NOTICE 'Table: crop_nutrient_requirements';
    RAISE NOTICE '========================================';
END $$;
