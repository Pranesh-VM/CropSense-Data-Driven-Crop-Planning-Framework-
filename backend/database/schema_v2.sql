-- ============================================================================
-- CropSense RINDM Cycle Management Database Schema - FIXED
-- PostgreSQL Database with Authentication and Real-time Cycle Tracking
-- ============================================================================

-- Drop existing tables
DROP TABLE IF EXISTS rainfall_events CASCADE;
DROP TABLE IF EXISTS nutrient_measurements CASCADE;
DROP TABLE IF EXISTS crop_cycles CASCADE;
DROP TABLE IF EXISTS fields CASCADE;
DROP TABLE IF EXISTS farmers CASCADE;
DROP TABLE IF EXISTS crop_nutrient_requirements CASCADE;
DROP TABLE IF EXISTS soil_test_recommendations CASCADE;
DROP TABLE IF EXISTS cycle_recommendations CASCADE;

-- ============================================================================
-- TABLE: farmers
-- ============================================================================
CREATE TABLE farmers (
    farmer_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_farmers_username ON farmers(username);
CREATE INDEX idx_farmers_email ON farmers(email);

-- ============================================================================
-- TABLE: fields
-- ============================================================================
CREATE TABLE fields (
    field_id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL DEFAULT 'Main Field',
    area_hectares DECIMAL(10, 2) DEFAULT 1.0,
    soil_type VARCHAR(20) CHECK (soil_type IN ('sandy', 'loamy', 'clay')),
    sand_percentage DECIMAL(5, 2),
    silt_percentage DECIMAL(5, 2),
    clay_percentage DECIMAL(5, 2),
    soil_ph DECIMAL(4, 2),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fields_farmer ON fields(farmer_id);

-- ============================================================================
-- TABLE: crop_nutrient_requirements
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
-- TABLE: crop_cycles
-- ============================================================================
CREATE TABLE crop_cycles (
    cycle_id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    field_id INTEGER REFERENCES fields(field_id),
    cycle_number INTEGER NOT NULL DEFAULT 1,
    crop_name VARCHAR(50) NOT NULL REFERENCES crop_nutrient_requirements(crop_name),
    start_date DATE NOT NULL,
    expected_end_date DATE,
    actual_end_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (
        status IN ('planning', 'active', 'completed', 'abandoned')
    ),
    initial_n_kg_ha DECIMAL(8, 2) NOT NULL,
    initial_p_kg_ha DECIMAL(8, 2) NOT NULL,
    initial_k_kg_ha DECIMAL(8, 2) NOT NULL,
    initial_ph DECIMAL(4, 2),
    current_n_kg_ha DECIMAL(8, 2) NOT NULL,
    current_p_kg_ha DECIMAL(8, 2) NOT NULL,
    current_k_kg_ha DECIMAL(8, 2) NOT NULL,
    final_n_kg_ha DECIMAL(8, 2),
    final_p_kg_ha DECIMAL(8, 2),
    final_k_kg_ha DECIMAL(8, 2),
    total_crop_uptake_n DECIMAL(8, 2) DEFAULT 0,
    total_crop_uptake_p DECIMAL(8, 2) DEFAULT 0,
    total_crop_uptake_k DECIMAL(8, 2) DEFAULT 0,
    total_rainfall_loss_n DECIMAL(8, 2) DEFAULT 0,
    total_rainfall_loss_p DECIMAL(8, 2) DEFAULT 0,
    total_rainfall_loss_k DECIMAL(8, 2) DEFAULT 0,
    soil_type VARCHAR(20),
    soil_ph DECIMAL(4, 2),
    last_weather_check TIMESTAMP,
    rainfall_event_count INTEGER DEFAULT 0,
    actual_yield_tonnes_ha DECIMAL(8, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cycles_farmer ON crop_cycles(farmer_id);
CREATE INDEX idx_cycles_status ON crop_cycles(status);

-- ============================================================================
-- TABLE: rainfall_events
-- ============================================================================
CREATE TABLE rainfall_events (
    event_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE,
    event_start TIMESTAMP NOT NULL,
    event_end TIMESTAMP,
    rainfall_mm DECIMAL(8, 2) NOT NULL,
    duration_hours DECIMAL(6, 2),
    intensity_mm_per_hour DECIMAL(8, 2),
    n_before_event DECIMAL(8, 2),
    p_before_event DECIMAL(8, 2),
    k_before_event DECIMAL(8, 2),
    nutrient_loss_n DECIMAL(8, 2) DEFAULT 0,
    nutrient_loss_p DECIMAL(8, 2) DEFAULT 0,
    nutrient_loss_k DECIMAL(8, 2) DEFAULT 0,
    n_after_event DECIMAL(8, 2),
    p_after_event DECIMAL(8, 2),
    k_after_event DECIMAL(8, 2),
    data_source VARCHAR(50) DEFAULT 'weather_api',
    api_response JSONB,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: cycle_recommendations
-- ============================================================================
CREATE TABLE cycle_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(farmer_id),
    cycle_id INTEGER REFERENCES crop_cycles(cycle_id),
    recommendation_type VARCHAR(20) CHECK (
        recommendation_type IN ('initial', 'next_cycle')
    ),
    n_kg_ha DECIMAL(8, 2),
    p_kg_ha DECIMAL(8, 2),
    k_kg_ha DECIMAL(8, 2),
    ph DECIMAL(4, 2),
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    rainfall DECIMAL(8, 2),
    crop_1 VARCHAR(50),
    crop_1_confidence DECIMAL(5, 4),
    crop_2 VARCHAR(50),
    crop_2_confidence DECIMAL(5, 4),
    crop_3 VARCHAR(50),
    crop_3_confidence DECIMAL(5, 4),
    selected_crop VARCHAR(50),
    selected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: nutrient_measurements
-- ============================================================================
CREATE TABLE nutrient_measurements (
    measurement_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE,
    measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    measurement_type VARCHAR(30),
    n_kg_ha DECIMAL(8, 2) NOT NULL,
    p_kg_ha DECIMAL(8, 2) NOT NULL,
    k_kg_ha DECIMAL(8, 2) NOT NULL,
    below_threshold BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- ============================================================================
-- TABLE: soil_test_recommendations
-- ============================================================================
CREATE TABLE soil_test_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    cycle_id INTEGER NOT NULL REFERENCES crop_cycles(cycle_id),
    farmer_id INTEGER NOT NULL REFERENCES farmers(farmer_id),
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(50),
    current_n_kg_ha DECIMAL(8, 2),
    current_p_kg_ha DECIMAL(8, 2),
    current_k_kg_ha DECIMAL(8, 2),
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP
);

-- ============================================================================
-- VIEWS
-- ============================================================================

CREATE VIEW active_cycles_status AS
SELECT
    cc.cycle_id,
    cc.farmer_id,
    f.username AS farmer_name,
    f.email,
    cc.crop_name,
    cc.start_date,
    cc.expected_end_date,
    cc.current_n_kg_ha,
    cc.current_p_kg_ha,
    cc.current_k_kg_ha,
    cc.rainfall_event_count,
    cc.last_weather_check
FROM crop_cycles cc
JOIN farmers f ON cc.farmer_id = f.farmer_id
WHERE cc.status = 'active';

CREATE VIEW farmer_dashboard AS
SELECT
    f.farmer_id,
    f.username,
    f.email,
    COUNT(DISTINCT cc.cycle_id) AS total_cycles,
    COUNT(DISTINCT CASE WHEN cc.status = 'active' THEN cc.cycle_id END) AS active_cycles,
    COUNT(DISTINCT CASE WHEN cc.status = 'completed' THEN cc.cycle_id END) AS completed_cycles,
    COUNT(DISTINCT re.event_id) AS total_rainfall_events
FROM farmers f
LEFT JOIN crop_cycles cc ON f.farmer_id = cc.farmer_id
LEFT JOIN rainfall_events re ON cc.cycle_id = re.cycle_id
GROUP BY f.farmer_id, f.username, f.email;
