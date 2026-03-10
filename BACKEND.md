# CropSense Backend Documentation

## Overview

CropSense is an AI-powered crop recommendation and planning system with three phases:

- **Phase 1**: Ensemble ML crop recommendation (99.55% accuracy)
- **Phase 2**: RINDM nutrient depletion tracking with weather integration
- **Phase 3**: Predictive planning with Monte Carlo simulation & Q-Learning

---

## Quick Start

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
..\venv\Scripts\Activate.ps1   # Windows
source ../venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements_v2.txt

# 4. Setup PostgreSQL database
psql -U postgres -f database/schema_v2.sql
psql -U postgres -d cropsense_db -f database/schema_v3_additions.sql

# 5. Run API server
python app_v2.py
# Server runs on http://localhost:5000
```

---

## Project Structure

```
backend/
├── app_v2.py                    # Main Flask API (Phase 1-3)
├── crop_recommendation.py       # Ensemble ML recommender
├── inference.py                 # CLI prediction tool
├── requirements_v2.txt          # Dependencies
├── .env                         # Environment config
│
├── database/
│   ├── schema_v2.sql            # Base database schema
│   ├── schema_v3_additions.sql  # Phase 3 tables
│   ├── db_utils.py              # Database connection manager
│   └── setup_database.py        # DB setup script
│
├── models/                      # Trained model files (.pkl)
│   └── q_agent.pkl              # Trained Q-Learning agent
│
└── src/
    ├── auth/
    │   └── auth.py              # JWT authentication
    │
    ├── data/
    │   └── preprocess.py        # Feature scaling/encoding
    │
    ├── models/
    │   ├── ensemble.py              # 4-model voting ensemble
    │   ├── rindm.py                 # Rainfall Nutrient Depletion Model
    │   ├── lstm_nutrient_predictor.py
    │   ├── prophet_nutrient_forecaster.py
    │   ├── state_transition_simulator.py
    │   ├── monte_carlo_simulator.py
    │   └── q_learning_agent.py
    │
    ├── services/
    │   ├── rindm_cycle_manager.py   # Crop cycle management
    │   └── weather_monitor.py       # Background weather tracking
    │
    └── utils/
        ├── crop_database.py         # Crop metadata
        ├── crop_nutrient_database.py # Nutrient uptake data
        └── weather_fetcher.py       # OpenWeatherMap integration
```

---

## API Endpoints

### Health Check
```
GET /health
```

### Authentication
```
POST /api/auth/signup    # Register new farmer
POST /api/auth/login     # Login
GET  /api/auth/profile   # Get profile (auth required)
```

### Prediction
```
POST /api/predict        # Single crop prediction (no auth)
```

### RINDM Cycle Management (Auth Required)
```
POST /api/rindm/get-recommendations     # Get top 3 crop recommendations
POST /api/rindm/start-cycle             # Start new crop cycle
GET  /api/rindm/active-cycle            # Get active cycle
GET  /api/rindm/cycle-status/{id}       # Get cycle status
POST /api/rindm/check-weather/{id}      # Manual weather check
GET  /api/rindm/history                 # Get cycle history
POST /api/rindm/complete-cycle/{id}     # Complete cycle
```

### Planning - Phase 3 (Auth Required)
```
POST /api/planning/compare-crops           # Compare crop trajectories
POST /api/planning/profit-risk-report      # Monte Carlo risk analysis
POST /api/planning/seasonal-rotation-plan  # Q-Learning optimal rotation
POST /api/planning/train-q-agent           # Train Q-Learning agent
```

---

## Environment Variables (.env)

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cropsense_db
DB_USER=postgres
DB_PASSWORD=your_password

# API Keys
OPENWEATHERMAP_API_KEY=your_api_key

# JWT
JWT_SECRET_KEY=your_secret_key

# Server
FLASK_PORT=5000
FLASK_ENV=development
ENABLE_WEATHER_MONITOR=true
WEATHER_CHECK_INTERVAL_MINUTES=60
```

---

## Database Schema

### Core Tables (Phase 1-2)
- `farmers` - User accounts
- `fields` - Farm field data
- `recommendations` - Crop recommendation history
- `crop_cycles` - Active/completed cycles
- `rainfall_events` - Weather event logs

### Phase 3 Tables
- `nutrient_timeseries_log` - Daily NPK tracking
- `market_prices` - Crop price history
- `cycle_performance_history` - Completed cycle metrics
- `qlearning_experiences` - RL experience buffer

---

## Key Modules

### 1. Ensemble Recommender
4-model soft voting ensemble: Random Forest, XGBoost, CatBoost, SVM
- Accuracy: 99.55%
- Input: N, P, K, pH, temperature, humidity, rainfall
- Output: Top 3 crop recommendations with confidence

### 2. RINDM Model
Rainfall Induced Nutrient Depletion Model
- Calculates nutrient loss from rainfall events
- Accounts for soil type (sandy/loamy/clay)
- Formula: Loss = Intensity × Soil_Coeff × Duration

### 3. State Transition Simulator
Core simulation engine: E(t+1) = f(E(t), A(t))
- Simulates soil state changes from crop choices
- Used by LSTM, Monte Carlo, Q-Learning

### 4. Monte Carlo Simulator
Probabilistic profit analysis
- 2000 simulations per crop
- Uncertainty: ±20% rainfall, ±15% price
- Returns: mean, std, risk-adjusted score

### 5. Q-Learning Agent
Optimal crop rotation planning
- State: Discretized N/P/K × 4 seasons
- Actions: 22 crops
- Hyperparameters: α=0.1, γ=0.9, ε=1.0→0.05

---

## Testing

```bash
# Run Phase 3 integration test
python test_phase3_integration.py

# Test individual modules
python -m src.models.monte_carlo_simulator
python -m src.models.q_learning_agent
```

---

## Dependencies

Key packages in `requirements_v2.txt`:
- Flask, flask-cors - Web API
- psycopg2 - PostgreSQL
- scikit-learn, xgboost, catboost - ML models
- tensorflow - LSTM
- prophet - Time series forecasting
- numpy, pandas - Data processing
- joblib - Model persistence
- requests - Weather API
- pyjwt - Authentication
