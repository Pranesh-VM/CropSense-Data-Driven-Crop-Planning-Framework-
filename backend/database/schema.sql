-- ============================================================================
-- CropSense Nutrient Management Database Schema
-- PostgreSQL Database
-- ============================================================================
-- 
-- Purpose: Track farmer nutrient levels, crop cycles, and rainfall impacts
-- 
-- Database: cropsense_db
-- Version: 1.0
-- Created: 2026-02-07
--
-- ============================================================================

-- Drop existing tables if needed (for fresh install)
DROP TABLE IF EXISTS rainfall_events CASCADE;
DROP TABLE IF EXISTS nutrient_measurements CASCADE;
DROP TABLE IF EXISTS crop_cycles CASCADE;
DROP TABLE IF EXISTS fields CASCADE;
DROP TABLE IF EXISTS farmers CASCADE;
DROP TABLE IF EXISTS crop_nutrient_requirements CASCADE;
DROP TABLE IF EXISTS soil_test_recommendations CASCADE;

-- ============================================================================
-- TABLE: farmers
-- Stores basic farmer information
-- ============================================================================
CREATE TABLE farmers (
    farmer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    location VARCHAR(200),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT farmers_phone_unique UNIQUE (phone),
    CONSTRAINT farmers_email_unique UNIQUE (email)
);

CREATE INDEX idx_farmers_location ON farmers(location);
CREATE INDEX idx_farmers_coordinates ON farmers(latitude, longitude);

COMMENT ON TABLE farmers IS 'Basic farmer profile information';
COMMENT ON COLUMN farmers.farmer_id IS 'Unique identifier (e.g., phone number or generated ID)';


-- ============================================================================
-- TABLE: fields
-- Stores information about farmers fields and soil properties
-- ============================================================================
CREATE TABLE fields (
    field_id SERIAL PRIMARY KEY,
    farmer_id VARCHAR(50) NOT NULL REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    area_hectares DECIMAL(10, 2) NOT NULL CHECK (area_hectares > 0),
    
    -- Soil properties
    soil_type VARCHAR(20) CHECK (soil_type IN ('sandy', 'loamy', 'clay')),
    sand_percentage DECIMAL(5, 2) CHECK (sand_percentage >= 0 AND sand_percentage <= 100),
    silt_percentage DECIMAL(5, 2) CHECK (silt_percentage >= 0 AND silt_percentage <= 100),
    clay_percentage DECIMAL(5, 2) CHECK (clay_percentage >= 0 AND clay_percentage <= 100),
    organic_matter_percentage DECIMAL(5, 2),
    soil_ph DECIMAL(4, 2) CHECK (soil_ph >= 0 AND soil_ph <= 14),
    
    -- Field characteristics
    slope_degrees DECIMAL(5, 2) DEFAULT 3.0,
    drainage_quality VARCHAR(20) CHECK (drainage_quality IN ('good', 'moderate', 'poor')),
    
    -- Location
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fields_texture_sum_check CHECK (
        (sand_percentage IS NULL) OR 
        (sand_percentage + silt_percentage + clay_percentage BETWEEN 99 AND 101)
    )
);

CREATE INDEX idx_fields_farmer ON fields(farmer_id);
CREATE INDEX idx_fields_soil_type ON fields(soil_type);

COMMENT ON TABLE fields IS 'Farmer field information with soil properties';
COMMENT ON COLUMN fields.soil_type IS 'Simple classification: sandy, loamy, or clay';
COMMENT ON COLUMN fields.sand_percentage IS 'Detailed texture: % sand (optional)';


-- ============================================================================
-- TABLE: crop_nutrient_requirements
-- Reference table for crop nutrient uptake data
-- ============================================================================
CREATE TABLE crop_nutrient_requirements (
    crop_name VARCHAR(50) PRIMARY KEY,
    n_uptake_kg_ha DECIMAL(8, 2) NOT NULL CHECK (n_uptake_kg_ha >= 0),
    p_uptake_kg_ha DECIMAL(8, 2) NOT NULL CHECK (p_uptake_kg_ha >= 0),
    k_uptake_kg_ha DECIMAL(8, 2) NOT NULL CHECK (k_uptake_kg_ha >= 0),
    cycle_days INTEGER NOT NULL CHECK (cycle_days > 0),
    average_yield_tonnes_ha DECIMAL(8, 2),
    data_source VARCHAR(200),
    
    -- Optimal growing conditions
    optimal_temp_min_c DECIMAL(5, 2),
    optimal_temp_max_c DECIMAL(5, 2),
    water_requirement_mm INTEGER,
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crop_requirements_name ON crop_nutrient_requirements(crop_name);

COMMENT ON TABLE crop_nutrient_requirements IS 'Nutrient uptake requirements for each crop type';
COMMENT ON COLUMN crop_nutrient_requirements.n_uptake_kg_ha IS 'Total nitrogen uptake in kg/ha';


-- ============================================================================
-- TABLE: crop_cycles
-- Tracks each growing season for a field
-- ============================================================================
CREATE TABLE crop_cycles (
    cycle_id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(field_id) ON DELETE CASCADE,
    crop_name VARCHAR(50) NOT NULL REFERENCES crop_nutrient_requirements(crop_name),
    
    -- Timing
    planting_date DATE NOT NULL,
    expected_harvest_date DATE,
    actual_harvest_date DATE,
    cycle_status VARCHAR(20) DEFAULT 'active' CHECK (
        cycle_status IN ('active', 'completed', 'abandoned')
    ),
    
    -- Initial nutrients (at planting)
    initial_n_kg_ha DECIMAL(8, 2) NOT NULL CHECK (initial_n_kg_ha >= 0),
    initial_p_kg_ha DECIMAL(8, 2) NOT NULL CHECK (initial_p_kg_ha >= 0),
    initial_k_kg_ha DECIMAL(8, 2) NOT NULL CHECK (initial_k_kg_ha >= 0),
    
    -- Final nutrients (at harvest)
    final_n_kg_ha DECIMAL(8, 2) CHECK (final_n_kg_ha >= 0),
    final_p_kg_ha DECIMAL(8, 2) CHECK (final_p_kg_ha >= 0),
    final_k_kg_ha DECIMAL(8, 2) CHECK (final_k_kg_ha >= 0),
    
    -- Cumulative losses
    total_rainfall_loss_n DECIMAL(8, 2) DEFAULT 0,
    total_rainfall_loss_p DECIMAL(8, 2) DEFAULT 0,
    total_rainfall_loss_k DECIMAL(8, 2) DEFAULT 0,
    
    -- Fertilizer applications (if any)
    fertilizer_applied_n DECIMAL(8, 2) DEFAULT 0,
    fertilizer_applied_p DECIMAL(8, 2) DEFAULT 0,
    fertilizer_applied_k DECIMAL(8, 2) DEFAULT 0,
    
    -- Yield
    actual_yield_tonnes_ha DECIMAL(8, 2),
    
    -- Metadata
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crop_cycles_field ON crop_cycles(field_id);
CREATE INDEX idx_crop_cycles_crop ON crop_cycles(crop_name);
CREATE INDEX idx_crop_cycles_status ON crop_cycles(cycle_status);
CREATE INDEX idx_crop_cycles_dates ON crop_cycles(planting_date, actual_harvest_date);

COMMENT ON TABLE crop_cycles IS 'Individual crop growing cycles with nutrient tracking';
COMMENT ON COLUMN crop_cycles.cycle_status IS 'active: growing, completed: harvested, abandoned: crop failed';


-- ============================================================================
-- TABLE: rainfall_events
-- Records rainfall events during crop cycles
-- ============================================================================
CREATE TABLE rainfall_events (
    event_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE,
    
    -- Rainfall data
    event_date DATE NOT NULL,
    rainfall_mm DECIMAL(8, 2) NOT NULL CHECK (rainfall_mm >= 0),
    duration_hours DECIMAL(6, 2) CHECK (duration_hours > 0),
    intensity_mm_per_hour DECIMAL(8, 2),
    
    -- Calculated losses (from RINDM)
    nutrient_loss_n DECIMAL(8, 2) DEFAULT 0 CHECK (nutrient_loss_n >= 0),
    nutrient_loss_p DECIMAL(8, 2) DEFAULT 0 CHECK (nutrient_loss_p >= 0),
    nutrient_loss_k DECIMAL(8, 2) DEFAULT 0 CHECK (nutrient_loss_k >= 0),
    
    -- Nutrients before this event
    n_before_event DECIMAL(8, 2),
    p_before_event DECIMAL(8, 2),
    k_before_event DECIMAL(8, 2),
    
    -- Data source
    data_source VARCHAR(50) DEFAULT 'weather_api' CHECK (
        data_source IN ('weather_api', 'farmer_reported', 'weather_station')
    ),
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rainfall_cycle ON rainfall_events(cycle_id);
CREATE INDEX idx_rainfall_date ON rainfall_events(event_date);

COMMENT ON TABLE rainfall_events IS 'Rainfall events and their impact on nutrients during crop cycles';
COMMENT ON COLUMN rainfall_events.data_source IS 'How rainfall was recorded: API, farmer input, or station';


-- ============================================================================
-- TABLE: nutrient_measurements
-- Track nutrient levels at different points in time
-- ============================================================================
CREATE TABLE nutrient_measurements (
    measurement_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE,
    
    -- Measurement details
    measurement_date DATE NOT NULL,
    measurement_type VARCHAR(30) CHECK (
        measurement_type IN ('initial', 'mid_season', 'final', 'soil_test', 'calculated')
    ),
    
    -- Nutrient levels
    n_kg_ha DECIMAL(8, 2) NOT NULL CHECK (n_kg_ha >= 0),
    p_kg_ha DECIMAL(8, 2) NOT NULL CHECK (p_kg_ha >= 0),
    k_kg_ha DECIMAL(8, 2) NOT NULL CHECK (k_kg_ha >= 0),
    
    -- Status flags
    n_status VARCHAR(20),
    p_status VARCHAR(20),
    k_status VARCHAR(20),
    needs_soil_test BOOLEAN DEFAULT FALSE,
    
    -- Source
    measurement_source VARCHAR(50) DEFAULT 'calculated' CHECK (
        measurement_source IN ('soil_test_lab', 'calculated', 'farmer_estimate')
    ),
    
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurements_cycle ON nutrient_measurements(cycle_id);
CREATE INDEX idx_measurements_date ON nutrient_measurements(measurement_date);
CREATE INDEX idx_measurements_type ON nutrient_measurements(measurement_type);

COMMENT ON TABLE nutrient_measurements IS 'Nutrient level measurements at different crop growth stages';
COMMENT ON COLUMN nutrient_measurements.measurement_type IS 'initial: planting, final: harvest, soil_test: lab test';


-- ============================================================================
-- TABLE: soil_test_recommendations
-- Store soil test alerts and fertilizer recommendations
-- ============================================================================
CREATE TABLE soil_test_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE,
    
    -- Recommendation details
    recommendation_date DATE NOT NULL,
    reason VARCHAR(50) CHECK (
        reason IN ('critical_nutrients', 'low_nutrients', 'pre_planting', 'routine')
    ),
    
    -- Critical nutrients
    critical_n BOOLEAN DEFAULT FALSE,
    critical_p BOOLEAN DEFAULT FALSE,
    critical_k BOOLEAN DEFAULT FALSE,
    
    -- Current levels when recommendation made
    current_n_kg_ha DECIMAL(8, 2),
    current_p_kg_ha DECIMAL(8, 2),
    current_k_kg_ha DECIMAL(8, 2),
    
    -- Recommended fertilizer amounts (if calculated)
    recommended_n_kg_ha DECIMAL(8, 2),
    recommended_p_kg_ha DECIMAL(8, 2),
    recommended_k_kg_ha DECIMAL(8, 2),
    
    -- Status
    recommendation_status VARCHAR(20) DEFAULT 'pending' CHECK (
        recommendation_status IN ('pending', 'acknowledged', 'completed', 'ignored')
    ),
    
    -- Follow-up
    farmer_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledgement_date TIMESTAMP,
    
    message TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recommendations_cycle ON soil_test_recommendations(cycle_id);
CREATE INDEX idx_recommendations_status ON soil_test_recommendations(recommendation_status);
CREATE INDEX idx_recommendations_date ON soil_test_recommendations(recommendation_date);

COMMENT ON TABLE soil_test_recommendations IS 'Soil test alerts and fertilizer recommendations';
COMMENT ON COLUMN soil_test_recommendations.reason IS 'Why recommendation was generated';


-- ============================================================================
-- TRIGGERS: Auto-update timestamps
-- ============================================================================

-- Function to update 'updated_date' timestamp
CREATE OR REPLACE FUNCTION update_updated_date_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_date = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER update_farmers_updated_date 
    BEFORE UPDATE ON farmers
    FOR EACH ROW EXECUTE FUNCTION update_updated_date_column();

CREATE TRIGGER update_fields_updated_date 
    BEFORE UPDATE ON fields
    FOR EACH ROW EXECUTE FUNCTION update_updated_date_column();

CREATE TRIGGER update_crop_cycles_updated_date 
    BEFORE UPDATE ON crop_cycles
    FOR EACH ROW EXECUTE FUNCTION update_updated_date_column();

CREATE TRIGGER update_crop_requirements_updated_date 
    BEFORE UPDATE ON crop_nutrient_requirements
    FOR EACH ROW EXECUTE FUNCTION update_updated_date_column();


-- ============================================================================
-- VIEWS: Useful queries for common operations
-- ============================================================================

-- Active crop cycles with current status
CREATE VIEW active_crop_cycles AS
SELECT 
    cc.cycle_id,
    f.farmer_id,
    fr.name AS farmer_name,
    f.field_name,
    cc.crop_name,
    cc.planting_date,
    cc.expected_harvest_date,
    CURRENT_DATE - cc.planting_date AS days_since_planting,
    cnr.cycle_days AS expected_cycle_days,
    cc.initial_n_kg_ha,
    cc.initial_p_kg_ha,
    cc.initial_k_kg_ha,
    COALESCE(cc.total_rainfall_loss_n, 0) AS total_rainfall_loss_n,
    COALESCE(cc.total_rainfall_loss_p, 0) AS total_rainfall_loss_p,
    COALESCE(cc.total_rainfall_loss_k, 0) AS total_rainfall_loss_k
FROM crop_cycles cc
JOIN fields f ON cc.field_id = f.field_id
JOIN farmers fr ON f.farmer_id = fr.farmer_id
JOIN crop_nutrient_requirements cnr ON cc.crop_name = cnr.crop_name
WHERE cc.cycle_status = 'active';

COMMENT ON VIEW active_crop_cycles IS 'Currently active crop growing cycles';


-- Nutrient status summary for active cycles
CREATE VIEW nutrient_status_summary AS
SELECT 
    cc.cycle_id,
    f.farmer_id,
    cc.crop_name,
    cc.planting_date,
    -- Calculate estimated current nutrients
    cc.initial_n_kg_ha - COALESCE(cc.total_rainfall_loss_n, 0) AS estimated_current_n,
    cc.initial_p_kg_ha - COALESCE(cc.total_rainfall_loss_p, 0) AS estimated_current_p,
    cc.initial_k_kg_ha - COALESCE(cc.total_rainfall_loss_k, 0) AS estimated_current_k,
    -- Thresholds
    CASE 
        WHEN (cc.initial_n_kg_ha - COALESCE(cc.total_rainfall_loss_n, 0)) < 30 THEN 'CRITICAL'
        WHEN (cc.initial_n_kg_ha - COALESCE(cc.total_rainfall_loss_n, 0)) < 60 THEN 'LOW'
        WHEN (cc.initial_n_kg_ha - COALESCE(cc.total_rainfall_loss_n, 0)) < 100 THEN 'MODERATE'
        ELSE 'GOOD'
    END AS n_status,
    CASE 
        WHEN (cc.initial_p_kg_ha - COALESCE(cc.total_rainfall_loss_p, 0)) < 10 THEN 'CRITICAL'
        WHEN (cc.initial_p_kg_ha - COALESCE(cc.total_rainfall_loss_p, 0)) < 20 THEN 'LOW'
        WHEN (cc.initial_p_kg_ha - COALESCE(cc.total_rainfall_loss_p, 0)) < 30 THEN 'MODERATE'
        ELSE 'GOOD'
    END AS p_status,
    CASE 
        WHEN (cc.initial_k_kg_ha - COALESCE(cc.total_rainfall_loss_k, 0)) < 40 THEN 'CRITICAL'
        WHEN (cc.initial_k_kg_ha - COALESCE(cc.total_rainfall_loss_k, 0)) < 80 THEN 'LOW'
        WHEN (cc.initial_k_kg_ha - COALESCE(cc.total_rainfall_loss_k, 0)) < 120 THEN 'MODERATE'
        ELSE 'GOOD'
    END AS k_status
FROM crop_cycles cc
JOIN fields f ON cc.field_id = f.field_id
WHERE cc.cycle_status = 'active';

COMMENT ON VIEW nutrient_status_summary IS 'Current nutrient status for active crops';


-- ============================================================================
-- STORED PROCEDURES: Common operations
-- ============================================================================

-- Function to calculate final nutrients after harvest
CREATE OR REPLACE FUNCTION calculate_final_nutrients(
    p_cycle_id INTEGER
)
RETURNS TABLE (
    final_n DECIMAL(8,2),
    final_p DECIMAL(8,2),
    final_k DECIMAL(8,2)
) AS $$
DECLARE
    v_initial_n DECIMAL(8,2);
    v_initial_p DECIMAL(8,2);
    v_initial_k DECIMAL(8,2);
    v_crop_uptake_n DECIMAL(8,2);
    v_crop_uptake_p DECIMAL(8,2);
    v_crop_uptake_k DECIMAL(8,2);
    v_rainfall_loss_n DECIMAL(8,2);
    v_rainfall_loss_p DECIMAL(8,2);
    v_rainfall_loss_k DECIMAL(8,2);
    v_fertilizer_n DECIMAL(8,2);
    v_fertilizer_p DECIMAL(8,2);
    v_fertilizer_k DECIMAL(8,2);
    v_crop_name VARCHAR(50);
BEGIN
    -- Get initial nutrients and crop info
    SELECT 
        cc.initial_n_kg_ha,
        cc.initial_p_kg_ha,
        cc.initial_k_kg_ha,
        cc.crop_name,
        COALESCE(cc.total_rainfall_loss_n, 0),
        COALESCE(cc.total_rainfall_loss_p, 0),
        COALESCE(cc.total_rainfall_loss_k, 0),
        COALESCE(cc.fertilizer_applied_n, 0),
        COALESCE(cc.fertilizer_applied_p, 0),
        COALESCE(cc.fertilizer_applied_k, 0)
    INTO 
        v_initial_n, v_initial_p, v_initial_k, v_crop_name,
        v_rainfall_loss_n, v_rainfall_loss_p, v_rainfall_loss_k,
        v_fertilizer_n, v_fertilizer_p, v_fertilizer_k
    FROM crop_cycles cc
    WHERE cc.cycle_id = p_cycle_id;
    
    -- Get crop uptake
    SELECT 
        n_uptake_kg_ha,
        p_uptake_kg_ha,
        k_uptake_kg_ha
    INTO
        v_crop_uptake_n,
        v_crop_uptake_p,
        v_crop_uptake_k
    FROM crop_nutrient_requirements
    WHERE crop_name = v_crop_name;
    
    -- Calculate: Final = Initial + Fertilizer - Crop Uptake - Rainfall Loss
    -- Ensure non-negative
    final_n := GREATEST(0, v_initial_n + v_fertilizer_n - v_crop_uptake_n - v_rainfall_loss_n);
    final_p := GREATEST(0, v_initial_p + v_fertilizer_p - v_crop_uptake_p - v_rainfall_loss_p);
    final_k := GREATEST(0, v_initial_k + v_fertilizer_k - v_crop_uptake_k - v_rainfall_loss_k);
    
    RETURN QUERY SELECT final_n, final_p, final_k;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_final_nutrients IS 'Calculate remaining nutrients after harvest for a crop cycle';


-- ============================================================================
-- SAMPLE DATA: Example farmer and field (for testing)
-- ============================================================================

-- Sample farmer
INSERT INTO farmers (farmer_id, name, phone, email, location, latitude, longitude)
VALUES 
    ('F001', 'Ramesh Kumar', '+919876543210', 'ramesh@example.com', 'Chennai, Tamil Nadu', 13.0827, 80.2707),
    ('F002', 'Priya Sharma', '+919876543211', 'priya@example.com', 'Coimbatore, Tamil Nadu', 11.0168, 76.9558);

-- Sample field
INSERT INTO fields (farmer_id, field_name, area_hectares, soil_type, soil_ph, latitude, longitude)
VALUES 
    (1, 'North Field', 2.5, 'loamy', 6.8, 13.0827, 80.2707),
    (2, 'Main Field', 3.0, 'clay', 7.2, 11.0168, 76.9558);


-- ============================================================================
-- Database Setup Complete
-- ============================================================================

COMMENT ON DATABASE cropsense_db IS 'CropSense Nutrient Management System Database v1.0';

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cropsense_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cropsense_user;
