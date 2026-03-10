-- ============================================================================
-- CropSense Schema v3 Additions
-- Run AFTER schema_v2.sql has already been applied
-- Phase 3: Predictive Planning & Profit Optimization Module
-- ============================================================================

-- Table 1: Daily nutrient time-series log (feeds LSTM training)
CREATE TABLE IF NOT EXISTS nutrient_timeseries_log (
    log_id              SERIAL PRIMARY KEY,
    cycle_id            INTEGER NOT NULL REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE,
    farmer_id           INTEGER NOT NULL REFERENCES farmers(farmer_id),
    log_date            DATE NOT NULL,
    n_kg_ha             DECIMAL(8,2),
    p_kg_ha             DECIMAL(8,2),
    k_kg_ha             DECIMAL(8,2),
    rainfall_mm         DECIMAL(8,2) DEFAULT 0,
    temperature_avg     DECIMAL(5,2),
    humidity_avg        DECIMAL(5,2),
    days_into_cycle     INTEGER,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cycle_id, log_date)
);

CREATE INDEX IF NOT EXISTS idx_ts_log_farmer ON nutrient_timeseries_log(farmer_id);
CREATE INDEX IF NOT EXISTS idx_ts_log_date   ON nutrient_timeseries_log(log_date);

-- Table 2: Market price history (feeds Prophet market forecasting)
CREATE TABLE IF NOT EXISTS market_prices (
    price_id        SERIAL PRIMARY KEY,
    crop_name       VARCHAR(50)  NOT NULL,
    price_date      DATE         NOT NULL,
    price_per_kg    DECIMAL(8,2) NOT NULL,
    market_name     VARCHAR(100),
    state_name      VARCHAR(50),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crop_name, price_date, market_name)
);

CREATE INDEX IF NOT EXISTS idx_market_crop ON market_prices(crop_name);
CREATE INDEX IF NOT EXISTS idx_market_date ON market_prices(price_date);

-- Table 3: Completed cycle performance history (feeds Q-Learning reward data)
CREATE TABLE IF NOT EXISTS cycle_performance_history (
    history_id          SERIAL PRIMARY KEY,
    farmer_id           INTEGER NOT NULL REFERENCES farmers(farmer_id),
    field_id            INTEGER REFERENCES fields(field_id),
    cycle_id            INTEGER REFERENCES crop_cycles(cycle_id),
    crop_name           VARCHAR(50)  NOT NULL,
    season              VARCHAR(20),               -- 'kharif','rabi','zaid','annual'
    start_date          DATE,
    end_date            DATE,
    duration_days       INTEGER,
    initial_n           DECIMAL(8,2),
    initial_p           DECIMAL(8,2),
    initial_k           DECIMAL(8,2),
    final_n             DECIMAL(8,2),
    final_p             DECIMAL(8,2),
    final_k             DECIMAL(8,2),
    total_rainfall_mm   DECIMAL(8,2),
    yield_kg_ha         DECIMAL(10,2),
    market_price_per_kg DECIMAL(8,2),
    profit_per_ha       DECIMAL(12,2),
    soil_penalty        DECIMAL(10,2),
    reward              DECIMAL(12,2),    -- profit_per_ha - soil_penalty
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cph_farmer ON cycle_performance_history(farmer_id);
CREATE INDEX IF NOT EXISTS idx_cph_crop   ON cycle_performance_history(crop_name);

-- Table 4: Q-Learning experience buffer (optional — for experience replay)
CREATE TABLE IF NOT EXISTS qlearning_experiences (
    exp_id          SERIAL PRIMARY KEY,
    farmer_id       INTEGER REFERENCES farmers(farmer_id),
    state_n         DECIMAL(8,2),
    state_p         DECIMAL(8,2),
    state_k         DECIMAL(8,2),
    state_season    INTEGER,         -- 0=Kharif, 1=Rabi, 2=Zaid, 3=Annual
    action_crop     VARCHAR(50),
    reward          DECIMAL(10,2),
    next_n          DECIMAL(8,2),
    next_p          DECIMAL(8,2),
    next_k          DECIMAL(8,2),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Verify tables were created
-- Run: \dt to list all tables
-- Expected: nutrient_timeseries_log, market_prices, 
--           cycle_performance_history, qlearning_experiences
-- ============================================================================
