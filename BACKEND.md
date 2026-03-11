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

---

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "message": "CropSense API is running",
  "services": {
    "authentication": "enabled",
    "single_prediction": "enabled",
    "rindm_cycles": "enabled",
    "weather_monitor": "enabled",
    "state_transition": "enabled",
    "monte_carlo": "enabled",
    "q_learning": "trained"
  }
}
```

---

### Authentication

#### POST /api/auth/signup

Register a new farmer account.

**Request:**
```json
{
  "username": "farmer123",
  "email": "farmer@example.com",
  "password": "password123",
  "phone": "+919876543210"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Farmer registered successfully",
  "farmer_id": 5,
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

#### POST /api/auth/login

Login to get JWT token.

**Request:**
```json
{
  "email": "farmer@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "farmer": {
    "farmer_id": 5,
    "username": "farmer123",
    "email": "farmer@example.com"
  }
}
```

---

#### GET /api/auth/profile

Get current user profile (requires auth).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "profile": {
    "farmer_id": 5,
    "username": "farmer123",
    "email": "farmer@example.com",
    "phone": "+919876543210",
    "created_at": "2026-03-01T10:30:00Z"
  }
}
```

---

### Prediction

#### POST /api/predict

Single crop prediction (no authentication required).

**Request:**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "latitude": 13.0827,
  "longitude": 80.2707
}
```

**Response (200):**
```json
{
  "top_3_crops": [
    {"crop": "rice", "confidence": 0.89},
    {"crop": "jute", "confidence": 0.06},
    {"crop": "cotton", "confidence": 0.03}
  ],
  "weather": {
    "temperature": 28.5,
    "humidity": 75,
    "rainfall": 150.2
  }
}
```

---

### RINDM Cycle Management (Auth Required)

All RINDM endpoints require: `Authorization: Bearer <token>`

---

#### POST /api/rindm/get-recommendations

Get top 3 crop recommendations for starting a cycle.

**Request:**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "latitude": 13.0827,
  "longitude": 80.2707
}
```

**Response (200):**
```json
{
  "success": true,
  "recommendation_id": 123,
  "recommendations": {
    "top_3_crops": [
      {"crop": "rice", "confidence": 0.89},
      {"crop": "jute", "confidence": 0.06},
      {"crop": "cotton", "confidence": 0.03}
    ]
  },
  "nutrients": {"N": 90, "P": 42, "K": 43, "ph": 6.5},
  "weather": {"temperature": 28.5, "humidity": 75, "rainfall": 150.2}
}
```

---

#### POST /api/rindm/start-cycle

Start a new RINDM crop cycle.

**Request:**
```json
{
  "recommendation_id": 123,
  "selected_crop": "rice",
  "soil_type": "loamy"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Crop cycle started successfully",
  "cycle_id": 45,
  "cycle_number": 3,
  "crop": "rice",
  "start_date": "2026-03-11",
  "expected_end_date": "2026-06-09",
  "initial_nutrients": {"N": 90, "P": 42, "K": 43},
  "thresholds": {"N": 30, "P": 10, "K": 40}
}
```

---

#### GET /api/rindm/active-cycle

Get farmer's currently active cycle.

**Response (200):**
```json
{
  "success": true,
  "has_active_cycle": true,
  "cycle": {
    "cycle_id": 45,
    "crop_name": "rice",
    "status": "active",
    "days_remaining": 75,
    "current_nutrients": {"N": 82.5, "P": 40.2, "K": 41.8},
    "nutrient_status": {
      "N": {"status": "good", "percentage": 91.7},
      "P": {"status": "good", "percentage": 95.7},
      "K": {"status": "good", "percentage": 97.2}
    },
    "rainfall_events": 3,
    "total_rainfall_mm": 45.2
  }
}
```

---

#### GET /api/rindm/cycle-status/{cycle_id}

Get detailed status of a specific cycle.

**Response (200):**
```json
{
  "success": true,
  "cycle_id": 45,
  "crop_name": "rice",
  "status": "active",
  "start_date": "2026-03-11",
  "expected_end_date": "2026-06-09",
  "days_elapsed": 15,
  "days_remaining": 75,
  "current_nutrients": {"N": 82.5, "P": 40.2, "K": 41.8},
  "initial_nutrients": {"N": 90, "P": 42, "K": 43},
  "thresholds": {"N": 30, "P": 10, "K": 40},
  "nutrient_status": {
    "N": {"current": 82.5, "threshold": 30, "status": "good", "percentage": 91.7},
    "P": {"current": 40.2, "threshold": 10, "status": "good", "percentage": 95.7},
    "K": {"current": 41.8, "threshold": 40, "status": "good", "percentage": 97.2}
  },
  "rainfall_summary": {
    "event_count": 3,
    "total_mm": 45.2,
    "total_loss": {"N": 5.4, "P": 1.2, "K": 0.9}
  }
}
```

---

#### POST /api/rindm/check-weather/{cycle_id}

Manually trigger weather check for a cycle.

**Response (200):**
```json
{
  "success": true,
  "message": "Weather check completed",
  "rainfall_detected": true,
  "rainfall_mm": 12.5,
  "nutrient_loss": {"N": 1.8, "P": 0.4, "K": 0.3},
  "updated_nutrients": {"N": 80.7, "P": 39.8, "K": 41.5}
}
```

---

#### GET /api/rindm/history

Get farmer's cycle history.

**Response (200):**
```json
{
  "success": true,
  "total": 5,
  "cycles": [
    {
      "cycle_id": 45,
      "cycle_number": 3,
      "crop_name": "rice",
      "status": "active",
      "start_date": "2026-03-11",
      "actual_end_date": null,
      "initial_n_kg_ha": 90,
      "final_n_kg_ha": null,
      "rainfall_event_count": 3
    },
    {
      "cycle_id": 32,
      "cycle_number": 2,
      "crop_name": "wheat",
      "status": "completed",
      "start_date": "2025-11-01",
      "actual_end_date": "2026-02-28",
      "initial_n_kg_ha": 85,
      "final_n_kg_ha": 42,
      "rainfall_event_count": 8
    }
  ]
}
```

---

#### POST /api/rindm/complete-cycle/{cycle_id}

Complete a cycle and get next recommendations.

**Response (200):**
```json
{
  "success": true,
  "message": "Cycle completed successfully",
  "cycle_id": 45,
  "final_nutrients": {"N": 35, "P": 28, "K": 38},
  "next_cycle_data": {
    "final_nutrients": {"N": 35, "P": 28, "K": 38, "ph": 6.5},
    "nutrients_too_low": true,
    "low_nutrients": ["Potassium (K)"],
    "fertilizer_recommendations": [
      {
        "nutrient": "Potassium",
        "current_level": 38,
        "recommended_addition": 22,
        "fertilizer_options": [
          "Muriate of Potash (0-0-60)",
          "Sulfate of Potash (0-0-50)",
          "Potassium Nitrate (13-0-44)"
        ]
      }
    ],
    "next_crop_recommendations": [
      {"crop": "mungbean", "confidence": 0.72},
      {"crop": "lentil", "confidence": 0.15},
      {"crop": "chickpea", "confidence": 0.08}
    ],
    "message": "Nutrients are too low for optimal crop growth. Consider applying fertilizers before starting a new cycle."
  }
}
```

---

### Planning - Phase 3 (Auth Required)

All planning endpoints require: `Authorization: Bearer <token>`

---

#### POST /api/planning/compare-crops

Compare soil trajectories for multiple crops using **HYBRID prediction** (LSTM + Formula).

**How it works:**
1. **Formula (RINDM)**: Deterministic calculation based on crop uptake + rainfall depletion
2. **LSTM**: Deep learning prediction trained on cross-field historical data
3. **Blended**: 60% LSTM + 40% Formula for best accuracy

**Note:** History is fetched internally from database - no user input needed.

**Request:**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "soil_type": "loamy",
  "season_index": 0,
  "expected_rainfall_mm": 600,
  "candidate_crops": ["rice", "wheat", "lentil"]
}
```

**Response (200) - With LSTM trained:**
```json
{
  "success": true,
  "lstm_available": true,
  "lstm_trained": true,
  "prediction_method": "lstm_blended",
  "blend_weights": {"lstm": 0.6, "formula": 0.4},
  "options": [
    {
      "crop": "rice",
      "season": "kharif",
      "initial_state": {"N": 90, "P": 42, "K": 43},
      "formula_prediction": {"N": 52.3, "P": 35.8, "K": 38.2},
      "lstm_prediction": {"N": 48.5, "P": 33.2, "K": 36.8},
      "final_state": {"N": 50.0, "P": 34.2, "K": 37.4},
      "prediction_method": "lstm_blended",
      "reward": 42500,
      "nutrient_balance_score": 0.72
    },
    {
      "crop": "wheat",
      "season": "kharif",
      "initial_state": {"N": 90, "P": 42, "K": 43},
      "formula_prediction": {"N": 58.1, "P": 38.2, "K": 40.5},
      "lstm_prediction": {"N": 55.2, "P": 36.5, "K": 38.8},
      "final_state": {"N": 56.4, "P": 37.2, "K": 39.5},
      "prediction_method": "lstm_blended",
      "reward": 38200,
      "nutrient_balance_score": 0.78
    },
    {
      "crop": "lentil",
      "season": "kharif",
      "initial_state": {"N": 90, "P": 42, "K": 43},
      "formula_prediction": {"N": 95.2, "P": 36.5, "K": 39.8},
      "lstm_prediction": {"N": 92.0, "P": 35.0, "K": 38.5},
      "final_state": {"N": 93.3, "P": 35.6, "K": 39.0},
      "prediction_method": "lstm_blended",
      "reward": 35800,
      "nutrient_balance_score": 0.85
    }
  ]
}
```

**Response (200) - Without LSTM (formula only):**
```json
{
  "success": true,
  "lstm_available": true,
  "lstm_trained": false,
  "prediction_method": "formula_only",
  "blend_weights": null,
  "options": [
    {
      "crop": "rice",
      "initial_state": {"N": 90, "P": 42, "K": 43},
      "formula_prediction": {"N": 52.3, "P": 35.8, "K": 38.2},
      "final_state": {"N": 52.3, "P": 35.8, "K": 38.2},
      "prediction_method": "formula_only",
      "reward": 42500
    }
  ]
}
```

---

#### POST /api/planning/profit-risk-report

Monte Carlo risk analysis (2000 simulations per crop).

**Request:**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "soil_type": "loamy",
  "expected_rainfall_mm": 600,
  "candidate_crops": ["rice", "wheat", "lentil"],
  "rainfall_uncertainty_pct": 0.20,
  "price_uncertainty_pct": 0.15
}
```

**Response (200):**
```json
{
  "success": true,
  "risk_profiles": [
    {
      "crop": "rice",
      "mean_profit": 42500,
      "std_profit": 8200,
      "min_profit": 18500,
      "max_profit": 68200,
      "percentile_5": 28500,
      "percentile_95": 56800,
      "prob_loss": 0.02,
      "sharpe_ratio": 5.18,
      "risk_adjusted_score": 0.82
    },
    {
      "crop": "wheat",
      "mean_profit": 38200,
      "std_profit": 6500,
      "min_profit": 21200,
      "max_profit": 55800,
      "percentile_5": 27500,
      "percentile_95": 49200,
      "prob_loss": 0.01,
      "sharpe_ratio": 5.88,
      "risk_adjusted_score": 0.85
    },
    {
      "crop": "lentil",
      "mean_profit": 35800,
      "std_profit": 5200,
      "min_profit": 22500,
      "max_profit": 48500,
      "percentile_5": 27200,
      "percentile_95": 44800,
      "prob_loss": 0.00,
      "sharpe_ratio": 6.88,
      "risk_adjusted_score": 0.88
    }
  ]
}
```

---

#### POST /api/planning/seasonal-rotation-plan

Get optimal multi-season rotation from Q-Learning agent.

**Request:**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "soil_type": "loamy",
  "expected_rainfall_mm": 600,
  "season_index": 0,
  "num_seasons": 5
}
```

**Response (200):**
```json
{
  "success": true,
  "plan": {
    "total_reward": 215800,
    "seasons": [
      {
        "season_num": 1,
        "season_name": "kharif",
        "crop": "rice",
        "start_state": {"N": 90, "P": 42, "K": 43},
        "end_state": {"N": 52, "P": 35, "K": 38},
        "reward": 42500
      },
      {
        "season_num": 2,
        "season_name": "rabi",
        "crop": "wheat",
        "start_state": {"N": 52, "P": 35, "K": 38},
        "end_state": {"N": 38, "P": 30, "K": 35},
        "reward": 38200
      },
      {
        "season_num": 3,
        "season_name": "zaid",
        "crop": "mungbean",
        "start_state": {"N": 38, "P": 30, "K": 35},
        "end_state": {"N": 55, "P": 25, "K": 32},
        "reward": 28500
      },
      {
        "season_num": 4,
        "season_name": "kharif",
        "crop": "cotton",
        "start_state": {"N": 55, "P": 25, "K": 32},
        "end_state": {"N": 35, "P": 18, "K": 25},
        "reward": 52800
      },
      {
        "season_num": 5,
        "season_name": "rabi",
        "crop": "chickpea",
        "start_state": {"N": 35, "P": 18, "K": 25},
        "end_state": {"N": 52, "P": 15, "K": 22},
        "reward": 53800
      }
    ]
  }
}
```

---

#### POST /api/planning/train-q-agent

Train the Q-Learning agent (takes 30-60 seconds).

**Request:**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "soil_type": "loamy",
  "expected_rainfall_mm": 600,
  "num_episodes": 2000,
  "crop_pool": ["rice", "wheat", "lentil", "maize", "mungbean", "chickpea"]
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Q-Agent trained for 2000 episodes",
  "model_saved_to": "backend/models/q_agent.pkl",
  "training_stats": {
    "episodes": 2000,
    "final_epsilon": 0.0500,
    "avg_reward_last_100": 43360.25,
    "q_table_nonzero": 1850
  }
}
```

---

> **Note: LSTM Auto-Training**
> 
> The LSTM model is trained **automatically** - no endpoint needed:
> 1. **On Startup**: If no model exists, trains on DB data (or synthetic data)
> 2. **After Cycles Complete**: Retrains every 5 completed crop cycles
> 
> Training uses **cross-field data** (all farmers) for better generalization.
> Model saved to: `backend/models/lstm_nutrient/`
> 
> To seed initial training data: `psql -d cropsense_db -f database/seed_training_data.sql`

---

#### GET /api/crop-info/{crop_name}

Get information about a specific crop.

**Response (200):**
```json
{
  "name": "rice",
  "season": "kharif",
  "duration_days": 120,
  "water_requirement": "high",
  "optimal_conditions": {
    "temperature": "20-35°C",
    "rainfall": "100-200mm/month",
    "ph": "5.5-7.0"
  },
  "nutrient_requirements": {
    "N": "80-120 kg/ha",
    "P": "40-60 kg/ha",
    "K": "40-60 kg/ha"
  }
}
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

### 6. LSTM Nutrient Predictor
Deep learning model trained on cross-field data
- Architecture: LSTM(64) → LSTM(32) → Dense(16) → Output
- Input: Last 30 days of [rainfall, temp, humidity, N, P, K]
- Output: Next 7-90 days nutrient prediction
- Training: Cross-field data from ALL farmers for better generalization
- Blending: 60% LSTM + 40% Formula (RINDM) for final predictions

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
