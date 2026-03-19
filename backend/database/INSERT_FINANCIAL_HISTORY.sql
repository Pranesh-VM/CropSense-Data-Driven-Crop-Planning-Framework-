-- ============================================================================
-- INSERT FINANCIAL HISTORY DATA (Farmer Demo Data)
-- ============================================================================
-- Run this in pgAdmin Query Tool on cropsense_db database
-- This inserts sample financial data for farmer_id=1
-- 
-- No table creation - uses existing storage or creates if needed
-- ============================================================================

-- Insert sample financial history records
-- Using only essential columns that exist in cycle_performance_history
INSERT INTO cycle_performance_history (
    farmer_id, field_id, crop_name, season, 
    start_date, end_date, duration_days,
    initial_n, initial_p, initial_k, final_n, final_p, final_k, 
    total_rainfall_mm, yield_kg_ha, market_price_per_kg, 
    profit_per_ha, soil_penalty, reward
)
VALUES
    -- Rice Demo Cycle - Kharif 2025 (June-October)
    (1, 1, 'Rice Demo', 'kharif', 
     '2025-06-01'::DATE, '2025-10-15'::DATE, 136,
     90.0, 42.0, 43.0, 25.0, 15.0, 18.0,
     650.0, 5500.0, 18.5,
     89000.0, 5000.0, 84000.0),
    
    -- Wheat Demo Cycle - Rabi 2025 (November-March)
    (1, 1, 'Wheat Demo', 'rabi',
     '2025-11-01'::DATE, '2026-03-20'::DATE, 140,
     85.0, 38.0, 40.0, 20.0, 12.0, 15.0,
     450.0, 4800.0, 21.0,
     95000.0, 4000.0, 91000.0),
    
    -- Maize Demo Cycle - Kharif 2025 (June-October)
    (1, 1, 'Maize Demo', 'kharif',
     '2025-06-15'::DATE, '2025-10-30'::DATE, 137,
     88.0, 40.0, 42.0, 22.0, 14.0, 16.0,
     700.0, 5200.0, 16.5,
     78000.0, 6000.0, 72000.0);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify the data was inserted:

-- 1. Check if records exist
-- SELECT COUNT(*) as total_records FROM cycle_performance_history WHERE farmer_id = 1;

-- 2. View all seeded data (what the endpoint should query)
-- SELECT 
--   cph.cycle_id,
--   cph.crop_name,
--   cc.start_date,
--   cc.actual_end_date as end_date,
--   COALESCE(cph.seed_cost_per_ha, 0) as seed_cost,
--   COALESCE(cph.fertilizer_cost_per_ha, 0) as fertilizer_cost,
--   COALESCE(cph.labour_cost_per_ha, 0) as labour_cost,
--   COALESCE(cph.profit_per_ha, 0) as profit
-- FROM cycle_performance_history cph
-- LEFT JOIN crop_cycles cc ON cph.cycle_id = cc.cycle_id
-- WHERE cph.farmer_id = 1
-- ORDER BY cph.start_date DESC;

-- 3. Calculate farmer totals
-- SELECT 
--   farmer_id,
--   COUNT(*) as total_cycles,
--   SUM(profit_per_ha) as total_profit,
--   AVG(profit_per_ha) as avg_profit,
--   MAX(profit_per_ha) as best_profit
-- FROM cycle_performance_history 
-- WHERE farmer_id = 1
-- GROUP BY farmer_id;

-- 4. Delete and re-insert if needed
-- DELETE FROM cycle_performance_history WHERE farmer_id = 1 AND crop_name IN ('Rice Demo', 'Wheat Demo', 'Maize Demo');
