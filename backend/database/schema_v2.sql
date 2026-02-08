-- ============================================================================
-- CropSense RINDM Cycle Management Database Schema - UPDATED
-- PostgreSQL Database with Authentication and Real-time Cycle Tracking
-- ============================================================================

-- Drop existing tables to recreate with new structure
DROP TABLE IF EXISTS rainfall_events CASCADE;
DROP TABLE IF EXISTS nutrient_measurements CASCADE;
DROP TABLE IF EXISTS crop_cycles CASCADE;
DROP TABLE IF EXISTS fields CASCADE;
DROP TABLE IF EXISTS farmers CASCADE;
DROP TABLE IF EXISTS crop_nutrient_requirements CASCADE;
DROP TABLE IF EXISTS soil_test_recommendations CASCADE;
DROP TABLE IF EXISTS cycle_recommendations CASCADE;

-- ============================================================================
-- TABLE: farmers (UPDATED with authentication)
-- ============================================================================
CREATE TABLE farmers (
    farmer_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Hashed password
    
    -- Profile information
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(200),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_farmers_username ON farmers(username);
CREATE INDEX idx_farmers_email ON farmers(email);
CREATE INDEX idx_farmers_location ON farmers(latitude, longitude);

COMMENT ON TABLE farmers IS 'Farmer accounts with authentication';


-- ============================================================================
-- TABLE: fields (Simplified - removed as we track nutrients in cycle)
-- Now just basic field info
-- ============================================================================
CREATE TABLE fields (
    field_id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL DEFAULT 'Main Field',
    area_hectares DECIMAL(10, 2) DEFAULT 1.0,
    
    -- Soil properties (can be updated before each cycle)
    soil_type VARCHAR(20) CHECK (soil_type IN ('sandy', 'loamy', 'clay')),
    sand_percentage DECIMAL(5, 2),
    silt_percentage DECIMAL(5, 2),
    clay_percentage DECIMAL(5, 2),
    soil_ph DECIMAL(4, 2),
    
    -- Location
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fields_farmer ON fields(farmer_id);


-- ============================================================================
-- TABLE: crop_nutrient_requirements (Same as before)
-- ============================================================================
CREATE TABLE crop_nutrient_requirements (
    crop_name VARCHAR(50) PRIMARY KEY,
    n_uptake_kg_ha DECIMAL(8, 2) NOT NULL,
    p_uptake_kg_ha DECIMAL(8, 2) NOT NULL,
    k_uptake_kg_ha DECIMAL(8, 2) NOT NULL,
    cycle_days INTEGER NOT NULL,
    average_yield_tonnes_ha DECIMAL(8, 2),
    optimal_temp_min_c DECIMAL(5, 2),
    optimal_temp_max_c DECIMAL(5, 2),
    water_requirement_mm INTEGER,
    data_source VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- TABLE: crop_cycles (UPDATED for real-time tracking)
-- ============================================================================
CREATE TABLE crop_cycles (
    cycle_id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    field_id INTEGER REFERENCES fields(field_id),
    
    -- Cycle info
    cycle_number INTEGER NOT NULL DEFAULT 1,  -- Track sequential cycles
    crop_name VARCHAR(50) NOT NULL REFERENCES crop_nutrient_requirements(crop_name),
    
    -- Timing
    start_date DATE NOT NULL,
    expected_end_date DATE,
    actual_end_date DATE,
    
    -- Cycle status
    status VARCHAR(20) DEFAULT 'active' CHECK (
        status IN ('planning', 'active', 'completed', 'abandoned')
    ),
    
    -- Initial nutrients (at start of THIS cycle)
    initial_n_kg_ha DECIMAL(8, 2) NOT NULL,
    initial_p_kg_ha DECIMAL(8, 2) NOT NULL,
    initial_k_kg_ha DECIMAL(8, 2) NOT NULL,
    initial_ph DECIMAL(4, 2),
    
    -- CURRENT nutrients (updated in real-time during cycle)
    current_n_kg_ha DECIMAL(8, 2) NOT NULL,
    current_p_kg_ha DECIMAL(8, 2) NOT NULL,
    current_k_kg_ha DECIMAL(8, 2) NOT NULL,
    
    -- Final nutrients (calculated at harvest)
    final_n_kg_ha DECIMAL(8, 2),
    final_p_kg_ha DECIMAL(8, 2),
    final_k_kg_ha DECIMAL(8, 2),
    
    -- Depletion tracking
    total_crop_uptake_n DECIMAL(8, 2) DEFAULT 0,
    total_crop_uptake_p DECIMAL(8, 2) DEFAULT 0,
    total_crop_uptake_k DECIMAL(8, 2) DEFAULT 0,
    
    total_rainfall_loss_n DECIMAL(8, 2) DEFAULT 0,
    total_rainfall_loss_p DECIMAL(8, 2) DEFAULT 0,
    total_rainfall_loss_k DECIMAL(8, 2) DEFAULT 0,
    
    -- Soil info for this cycle
    soil_type VARCHAR(20),
    soil_ph DECIMAL(4, 2),
    
    -- Weather monitoring
    last_weather_check TIMESTAMP,
    rainfall_event_count INTEGER DEFAULT 0,
    
    -- Yield
    actual_yield_tonnes_ha DECIMAL(8, 2),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cycles_farmer ON crop_cycles(farmer_id);
CREATE INDEX idx_cycles_status ON crop_cycles(status);
CREATE INDEX idx_cycles_dates ON crop_cycles(start_date, actual_end_date);
CREATE INDEX idx_cycles_active ON crop_cycles(farmer_id, status) WHERE status = 'active';

COMMENT ON TABLE crop_cycles IS 'Individual crop cycles with real-time nutrient tracking';
COMMENT ON COLUMN crop_cycles.current_n_kg_ha IS 'Real-time nutrient level, updated as rainfall occurs';


-- ============================================================================
-- TABLE: rainfall_events (UPDATED with automatic detection)
-- ============================================================================
CREATE TABLE rainfall_events (
    event_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE,
    
    -- Rainfall data
    event_start TIMESTAMP NOT NULL,
    event_end TIMESTAMP,
    rainfall_mm DECIMAL(8, 2) NOT NULL,
    duration_hours DECIMAL(6, 2),
    intensity_mm_per_hour DECIMAL(8, 2),
    
    -- Nutrients BEFORE this event
    n_before_event DECIMAL(8, 2),
    p_before_event DECIMAL(8, 2),
    k_before_event DECIMAL(8, 2),
    
    -- Calculated losses (from RINDM)
    nutrient_loss_n DECIMAL(8, 2) DEFAULT 0,
    nutrient_loss_p DECIMAL(8, 2) DEFAULT 0,
    nutrient_loss_k DECIMAL(8, 2) DEFAULT 0,
    
    -- Nutrients AFTER this event
    n_after_event DECIMAL(8, 2),
    p_after_event DECIMAL(8, 2),
    k_after_event DECIMAL(8, 2),
    
    -- Source
    data_source VARCHAR(50) DEFAULT 'weather_api',
    api_response JSONB,  -- Store raw API response
    
    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rainfall_cycle ON rainfall_events(cycle_id);
CREATE INDEX idx_rainfall_date ON rainfall_events(event_start);
CREATE INDEX idx_rainfall_unprocessed ON rainfall_events(cycle_id, processed) WHERE processed = FALSE;


-- ============================================================================
-- TABLE: cycle_recommendations (NEW - stores top 3 crop recommendations)
-- ============================================================================
CREATE TABLE cycle_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(farmer_id),
    cycle_id INTEGER REFERENCES crop_cycles(cycle_id),
    
    -- Context
    recommendation_type VARCHAR(20) CHECK (
        recommendation_type IN ('initial', 'next_cycle')
    ),
    
    -- Nutrient levels at time of recommendation
    n_kg_ha DECIMAL(8, 2),
    p_kg_ha DECIMAL(8, 2),
    k_kg_ha DECIMAL(8, 2),
    ph DECIMAL(4, 2),
    
    -- Weather data used
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    rainfall DECIMAL(8, 2),
    
    -- Top 3 recommendations
    crop_1 VARCHAR(50),
    crop_1_confidence DECIMAL(5, 4),
    crop_2 VARCHAR(50),
    crop_2_confidence DECIMAL(5, 4),
    crop_3 VARCHAR(50),
    crop_3_confidence DECIMAL(5, 4),
    
    -- Selection
    selected_crop VARCHAR(50),
    selected_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recommendations_farmer ON cycle_recommendations(farmer_id);
CREATE INDEX idx_recommendations_cycle ON cycle_recommendations(cycle_id);


-- ============================================================================
-- TABLE: nutrient_measurements (historical tracking)
-- ============================================================================
CREATE TABLE nutrient_measurements (
    measurement_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE,
    
    -- Measurement details
    measurement_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    measurement_type VARCHAR(30) CHECK (
        measurement_type IN ('cycle_start', 'rainfall_update', 'daily_check', 'cycle_end')
    ),
    
    -- Nutrient levels
    n_kg_ha DECIMAL(8, 2) NOT NULL,
    p_kg_ha DECIMAL(8, 2) NOT NULL,
    k_kg_ha DECIMAL(8, 2) NOT NULL,
    
    -- Status
    n_status VARCHAR(20),
    p_status VARCHAR(20),
    k_status VARCHAR(20),
    below_threshold BOOLEAN DEFAULT FALSE,
    
    notes TEXT
);

CREATE INDEX idx_measurements_cycle ON nutrient_measurements(cycle_id);
CREATE INDEX idx_measurements_date ON nutrient_measurements(measurement_date);


-- ============================================================================
-- TABLE: soil_test_recommendations (warnings)
-- ============================================================================
CREATE TABLE soil_test_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id),
    farmer_id INTEGER NOT NULL REFERENCES farmers(farmer_id),
    
    recommendation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(50),
    
    critical_n BOOLEAN DEFAULT FALSE,
    critical_p BOOLEAN DEFAULT FALSE,
    critical_k BOOLEAN DEFAULT FALSE,
    
    current_n_kg_ha DECIMAL(8, 2),
    current_p_kg_ha DECIMAL(8, 2),
    current_k_kg_ha DECIMAL(8, 2),
    
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP
);

CREATE INDEX idx_soil_test_farmer ON soil_test_recommendations(farmer_id);
CREATE INDEX idx_soil_test_pending ON soil_test_recommendations(status) WHERE status = 'pending';


-- ============================================================================
-- TRIGGERS: Auto-update timestamps
-- ============================================================================
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_farmers_timestamp 
    BEFORE UPDATE ON farmers
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_fields_timestamp 
    BEFORE UPDATE ON fields
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_cycles_timestamp 
    BEFORE UPDATE ON crop_cycles
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();


-- ============================================================================
-- FUNCTIONS: Business logic
-- ============================================================================

-- Function to check if nutrients are below threshold
CREATE OR REPLACE FUNCTION check_nutrient_threshold(
    n_value DECIMAL,
    p_value DECIMAL,
    k_value DECIMAL
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (n_value < 30 OR p_value < 10 OR k_value < 40);
END;
$$ LANGUAGE plpgsql;


-- Function to get farmer's active cycle
CREATE OR REPLACE FUNCTION get_active_cycle(p_farmer_id INTEGER)
RETURNS TABLE (
    cycle_id INTEGER,
    crop_name VARCHAR(50),
    start_date DATE,
    current_n DECIMAL(8,2),
    current_p DECIMAL(8,2),
    current_k DECIMAL(8,2),
    days_remaining INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cc.cycle_id,
        cc.crop_name,
        cc.start_date,
        cc.current_n_kg_ha,
        cc.current_p_kg_ha,
        cc.current_k_kg_ha,
        (cc.expected_end_date - CURRENT_DATE)::INTEGER as days_remaining
    FROM crop_cycles cc
    WHERE cc.farmer_id = p_farmer_id 
      AND cc.status = 'active'
    ORDER BY cc.start_date DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- VIEWS: Useful queries
-- ============================================================================

-- Active cycles with current status
CREATE VIEW active_cycles_status AS
SELECT 
    cc.cycle_id,
    cc.farmer_id,
    f.name as farmer_name,
    f.email,
    cc.cycle_number,
    cc.crop_name,
    cc.start_date,
    cc.expected_end_date,
    (CURRENT_DATE - cc.start_date) AS days_elapsed,
    (cc.expected_end_date - CURRENT_DATE) AS days_remaining,
    cc.current_n_kg_ha,
    cc.current_p_kg_ha,
    cc.current_k_kg_ha,
    CASE 
        WHEN cc.current_n_kg_ha < 30 OR cc.current_p_kg_ha < 10 OR cc.current_k_kg_ha < 40 
        THEN TRUE ELSE FALSE 
    END as below_threshold,
    cc.rainfall_event_count,
    cc.last_weather_check
FROM crop_cycles cc
JOIN farmers f ON cc.farmer_id = f.farmer_id
WHERE cc.status = 'active';

COMMENT ON VIEW active_cycles_status IS 'Real-time status of all active crop cycles';


-- Farmer dashboard view
CREATE VIEW farmer_dashboard AS
SELECT 
    f.farmer_id,
    f.name,
    f.email,
    COUNT(DISTINCT cc.cycle_id) as total_cycles,
    COUNT(DISTINCT CASE WHEN cc.status = 'active' THEN cc.cycle_id END) as active_cycles,
    COUNT(DISTINCT CASE WHEN cc.status = 'completed' THEN cc.cycle_id END) as completed_cycles,
    MAX(cc.cycle_number) as current_cycle_number,
    COUNT(DISTINCT re.event_id) as total_rainfall_events
FROM farmers f
LEFT JOIN crop_cycles cc ON f.farmer_id = cc.farmer_id
LEFT JOIN rainfall_events re ON cc.cycle_id = re.cycle_id
GROUP BY f.farmer_id, f.name, f.email;

COMMENT ON VIEW farmer_dashboard IS 'Summary statistics for farmer dashboard';


-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Sample farmer (password: 'password123' - hashed with bcrypt)
INSERT INTO farmers (username, email, password_hash, name, phone, location, latitude, longitude)
VALUES 
    ('testfarmer', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS7NU/fhe', 
     'Test Farmer', '+919876543210', 'Chennai, Tamil Nadu', 13.0827, 80.2707);

-- Sample field
INSERT INTO fields (farmer_id, field_name, area_hectares, soil_type, soil_ph, latitude, longitude)
VALUES (1, 'Main Field', 2.0, 'loamy', 6.8, 13.0827, 80.2707);


-- ============================================================================
-- Setup Complete
-- ============================================================================
COMMENT ON DATABASE cropsense_db IS 'CropSense RINDM Cycle Management System v2.0';
