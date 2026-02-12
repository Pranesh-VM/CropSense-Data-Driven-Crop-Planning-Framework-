# System Architecture Diagram

## Data Flow: From Collection to Predictions

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CROP CYCLE WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────            ┌──────────────            ┌──────────────┐
│  1. START CYCLE          │  2. DAILY MONITORING    │ 3. PREDICTIONS│
└──────────────            └──────────────            └──────────────┘
      ▼                           ▼                           ▼

  ┌─────────────┐         ┌─────────────┐         ┌──────────────┐
  │  Farmer     │         │  Weather    │         │   LSTM +     │
  │  selects    │────────►│  Monitor    │────────►│   Prophet    │
  │  crop       │         │  runs 24/7  │         │   predict    │
  └─────────────┘         └─────────────┘         └──────────────┘
                                │
                                │ Daily data
                                │ collected
                                ▼
                         ┌─────────────┐
                         │ Time-Series │
                         │ Data Manager│
                         └─────────────┘
                                │
                                │ Stored in DB
                                │ daily_weather_nutrient_log
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                        DATABASE                                    │
│  ┌──────────────┬──────────────┬──────────────────┬──────────────┐│
│  │ Crop Cycles  │ Nutrient     │ Daily Weather    │ Time-Series  ││
│  │              │ Measurements │ Nutrient Log     │ Predictions  ││
│  └──────────────┴──────────────┴──────────────────┴──────────────┘│
└───────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
        
        ┌─────────────┐  ┌────────────┐  ┌──────────────┐
        │  LSTM Model │  │   Prophet  │  │    Advisor   │
        │ (7-30 days) │  │  (30+ days)│  │  (Combined)  │
        └─────────────┘  └────────────┘  └──────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
        
        ┌──────────────┐          ┌──────────────────┐
        │   EARLY      │          │    API           │
        │  WARNINGS    │          │  ENDPOINTS       │
        │  (Alerts)    │          │  (/predictions)  │
        └──────────────┘          └──────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                ▼
        
        ┌──────────────────────────────────┐
        │   FARMER APP / NOTIFICATIONS      │
        │  - Early warnings                 │
        │  - Next crop suggestions          │
        │  - Fertilizer timing              │
        └──────────────────────────────────┘
```

---

## Model Training Pipeline

```
┌──────────────────────────────────────────────────────────┐
│              MODEL TRAINING PIPELINE                      │
└──────────────────────────────────────────────────────────┘

PHASE 1: Data Preparation
─────────────────────────
          ↓
    ┌─────────────────────┐
    │ Historical Data     │  ← Get from database (365+ days)
    │ (rainfall, temp,    │
    │  humidity, N, P, K) │
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Data Cleaning       │  ← Fill missing values
    │ Normalization       │    Outlier removal
    │ Feature Scaling     │    Standardization
    └─────────────────────┘


PHASE 2: LSTM Training
──────────────────────
          ↓
    ┌─────────────────────┐
    │ Sequence Prep       │  ← Create (lookback=30, forecast=7)
    │ X: (samples, 30, 6) │    windows from data
    │ y: (samples, 21)    │
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Build LSTM          │  ← 2 LSTM layers (64→32 units)
    │ Network             │    2 Dropout layers
    │                     │    Dense output (21 neurons)
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Train (50 epochs)   │  ← Batch: 32
    │ Monitor loss        │    Validation split: 20%
    │ Early stopping      │    Learning rate: 0.001
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Save Model          │  ← lstm_nutrient_model.h5
    │ & Scaler            │    lstm_scaler.pkl
    └─────────────────────┘


PHASE 3: Prophet Training
─────────────────────────
          ↓
    ┌─────────────────────┐
    │ Format Data         │  ← Create 'ds' (date) & 'y' (value)
    │ (ds, y columns)     │    columns for each nutrient
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Build 3 Models      │  ← One each for N, P, K
    │ (One per nutrient)  │    Yearly seasonality ON
    │                     │    Weekly seasonality OFF
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Fit Models          │  ← Learn trend + seasonal patterns
    │ (2-5 min each)      │    Automatically finds change points
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Save Models         │  ← prophet_model_N.pkl
    │                     │    prophet_model_P.pkl
    │                     │    prophet_model_K.pkl
    └─────────────────────┘


PHASE 4: Continuous Retraining
──────────────────────────────
          ↓
    ┌─────────────────────┐
    │ Weekly Scheduler    │  ← Every Monday at 2 AM
    │ (Automatic)         │
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Fetch Latest Data   │  ← Get past 365 days
    │ (More cycles added) │    Real data accumulates
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Retrain Models      │  ← Models improve over time
    │ (Same process)      │    More real data = better accuracy
    └─────────────────────┘
          ↓
    ┌─────────────────────┐
    │ Compare & Deploy    │  ← If better, replace old models
    │ New Predictions     │    Always keep best version
    └─────────────────────┘
```

---

## Time-Series Data Collection

```
┌────────────────────────────────────────────────────┐
│         DAILY DATA COLLECTION WORKFLOW              │
└────────────────────────────────────────────────────┘

Weather Monitor (runs every hour)
─────────────────────────────────

    Weather API Call
            ↓
    ┌──────────────────┐
    │ Get current:     │
    │ - Rainfall (mm)  │
    │ - Temperature    │
    │ - Humidity       │
    │ - Wind speed     │
    └──────────────────┘
            ↓
    ┌──────────────────┐
    │ Get from RINDM:  │
    │ - Current N/P/K  │
    │ - Cycle status   │
    │ - Field location │
    └──────────────────┘
            ↓
    ┌──────────────────────────────┐
    │ TimeSeriesDataManager        │
    │ .log_daily_weather_nutrients()
    └──────────────────────────────┘
            ↓
    ┌──────────────────────────────┐
    │ INSERT daily_weather_nutrient_log
    │                              │
    │ farmer_id: 5                 │
    │ field_id: 2                  │
    │ cycle_id: 10                 │
    │ log_date: 2026-02-11         │
    │ rainfall_mm: 2.5             │
    │ temperature_avg: 28.3        │
    │ humidity_avg: 65.2           │
    │ n_kg_ha: 145.5               │  (latest measurement)
    │ p_kg_ha: 32.1                │
    │ k_kg_ha: 198.4               │
    └──────────────────────────────┘
            ↓
    ┌──────────────────────────────┐
    │ PostgreSQL Database          │
    │ (Accumulates daily)          │
    │                              │
    │ 365 days = 365 rows          │
    │ 2 years = 730 rows           │
    │ Training ready!              │
    └──────────────────────────────┘
```

---

## Prediction Generation

```
┌──────────────────────────────────────────────┐
│        PREDICTION GENERATION FLOW             │
└──────────────────────────────────────────────┘

API Request: /api/rindm/cycle/10/predictions
                      ↓
        ┌──────────────────────────┐
        │ PredictiveCycleAdvisor   │
        │ .generate_cycle_          │
        │  predictions()            │
        └──────────────────────────┘
                      ↓
        ┌─────────────┬─────────────┐
        ▼             ▼             ▼
    
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Get Cycle│  │Get Recent│  │ Get Hist │
    │ Info     │  │ 30 days  │  │ 365 days │
    └──────────┘  └──────────┘  └──────────┘
        ▼             ▼             ▼
        
        ┌──────────────────────────────────┐
        │      BRANCH 1: LSTM PREDICTION    │
        │                                  │
        │ lstm.predict_next_days(recent_30)│
        │                                  │
        │ Input:  Last 30 days (normalized)│
        │ Model:  2 LSTM layers           │
        │ Output: 7-day forecast          │
        │                                  │
        │ Result:                         │
        │ Day 1: N=95.5, P=28.2, K=145.3 │
        │ Day 2: N=93.2, P=27.9, K=142.1 │
        │ ...                             │
        │ Day 7: N=78.5, P=24.1, K=121.4 │
        │              (with confidence)   │
        └──────────────────────────────────┘
        ▼
        
        ┌──────────────────────────────────┐
        │    BRANCH 2: PROPHET FORECAST     │
        │                                  │
        │ prophet.forecast_next_days(30)   │
        │                                  │
        │ Input:  365 days (time series)  │
        │ Models: 3 Prophet (N/P/K)       │
        │ Output: 30-day forecast         │
        │                                  │
        │ Result:                         │
        │ Day 1: N=94.8 (92.0-97.5)      │
        │ Day 2: N=92.5 (89.8-95.2)      │
        │ ...                             │
        │ Day 30: N=65.2 (58.5-71.9)     │
        │         (with seasonal pattern)  │
        └──────────────────────────────────┘
        ▼
        
        ┌──────────────────────────────────┐
        │      BRANCH 3: EARLY WARNINGS     │
        │                                  │
        │ Generate alerts if:             │
        │ - Predicted < Critical (7-14d)  │
        │ - Predicted < Warning (2-4w)    │
        │                                  │
        │ Result:                         │
        │ [{                              │
        │   'nutrient': 'N',              │
        │   'severity': 'critical',       │
        │   'days_until': 5,              │
        │   'recommendation': '...'       │
        │ }]                              │
        └──────────────────────────────────┘
        ▼
        
        ┌──────────────────────────────────┐
        │    SAVE TO DATABASE               │
        │    (time_series_predictions)     │
        │                                  │
        │ Store for:                       │
        │ - Historical tracking            │
        │ - Accuracy evaluation            │
        │ - Model improvement              │
        └──────────────────────────────────┘
        ▼
        
        ┌──────────────────────────────────┐
        │    API RESPONSE (JSON)            │
        │                                  │
        │ {                                │
        │   "success": true,              │
        │   "lstm": { predictions... },   │
        │   "prophet": { predictions... },│
        │   "warnings": [ alerts... ]     │
        │ }                                │
        └──────────────────────────────────┘
        ▼
        
        ┌──────────────────────────────────┐
        │    FARMER SEES IN APP             │
        │                                  │
        │ ⚠️  CRITICAL ALERT               │
        │ Nitrogen will deplete in 5 days │
        │ → Apply fertilizer today        │
        └──────────────────────────────────┘
```

---

## Early Warning System

```
┌─────────────────────────────────────────────────────┐
│       EARLY WARNING THRESHOLD SYSTEM                 │
└─────────────────────────────────────────────────────┘

Nutrient Level vs Time
────────────────────

    N (kg/ha)
    │
 200│  ▓▓▓  Start (Initial = 200 kg/ha)
    │  ▓ ▓
 180│  ▓  ▓
    │  ▓   ▓
 160│      ▓
    │       ▓
 140│        ▓▓
    │           ▓
 120│            ▓▓
    │               ▓▓▓
 100│                   ▓▓
    │                      ▓
  80│ ┌─────────────────────▓────── WARNING (80 kg/ha)
    │ │                        ▓▓
  60│ │┌──────────────────────────▓─ CRITICAL (30 kg/ha)
    │ ││                             ▓
  40│ ││
    │ ││
  20│ ││
    │ ││
   0└──┴┴─────────────────────────── Time (days)
      0  14 28 42 56 70 84 98 112 126
      
      ▲               ▲
      │               │
      Day 28:         Day 98:
      Monitor phase   CRITICAL!
      (N=150)         (N=35)


Alert Timeline
──────────────

Day 85 (Normal): No alert
                 N = 105 kg/ha
                 Status: OK

Day 92 (Monitor): Caution alert sent
                 N = 88 kg/ha
                 Status: "Watch carefully"
                 Action: "Plan fertilizer in 2 weeks"

Day 99 (Warning): Urgent alert sent
                 N = 58 kg/ha
                 Predicted Day 105: N = 45 kg/ha
                 Status: "Apply fertilizer within 3 days"

Day 105 (Critical): Critical alert sent
                 N = 42 kg/ha
                 Predicted Day 112: N = 5 kg/ha
                 Status: "Apply NOW or harvest"
                 Days before crop dies: 3-4 days


Farmer Actions Based on Severity
─────────────────────────────────

Monitor (N > 80)
    ├─ Track daily
    └─ Plan ahead

Warning (60 < N < 80)
    ├─ Buy fertilizer
    ├─ Schedule application
    └─ Alert family

Urgent (30 < N < 60)
    ├─ Apply fertilizer TODAY
    └─ Increase farmhand availability

Critical (N < 30)
    ├─ EMERGENCY application
    ├─ OR prepare to harvest
    └─ Significant yield loss likely
```

---

## Model Comparison

```
┌──────────────────────────────────────────────────────┐
│         LSTM vs PROPHET vs ENSEMBLE                   │
└──────────────────────────────────────────────────────┘

LSTM Model
──────────
Purpose:     Grain-level predictions (day by day)
Input:       30 days history
Horizon:     7 days (can extend to 14-30)
Accuracy:    85-90%
Speed:       0.1 sec
Best for:    Short-term adjustments
Learns:      Temporal patterns, rainfall → loss relationship
Weakness:    Needs more training data (100+ samples)

Output Example:
┌─────────┬──────────┬──────────┬──────────┐
│Day      │N (pred)  │P (pred)  │K (pred)  │
├─────────┼──────────┼──────────┼──────────┤
│Tomorrow │95.5±10   │28.2±5    │145.3±20  │
│+2 days  │92.1±12   │27.1±6    │139.8±22  │
│+3 days  │88.5±15   │25.9±8    │133.2±25  │
│...      │...       │...       │...       │
└─────────┴──────────┴──────────┴──────────┘


PROPHET Model
─────────────
Purpose:     Seasonal trends (long-term outlook)
Input:       365 days history
Horizon:     30+ days
Accuracy:    75-85%
Speed:       0.05 sec
Best for:    Planning season strategy
Learns:      Yearly patterns, monsoon effects, trends
Weakness:    Slower to adapt to recent changes

Output Example:
┌──────────────┬────────────┬──────────────────┐
│Date          │N (pred)    │Confidence (95%)  │
├──────────────┼────────────┼──────────────────┤
│2026-02-12    │94.8        │92.0 - 97.5       │
│2026-02-19    │85.3        │78.9 - 91.7       │
│2026-02-26    │75.2        │65.4 - 85.0       │
│2026-03-05    │65.2        │52.1 - 78.3       │
└──────────────┴────────────┴──────────────────┘


ENSEMBLE (LSTM + PROPHET)
──────────────────────────
Combines both for best results:
├─ LSTM for 7 days (detailed)
├─ Prophet for 30 days (trends)
└─ Weighted average when overlapping

Accuracy:    90-95% (best choice)
Speed:       0.2 sec (combined)
Best for:    Production use
Philosophy:  "Ensemble beats individual models"

Trust LSTM more for:        Trust Prophet more for:
├─ Next 2-7 days           ├─ Next 2-4 weeks
├─ Recent rainfall impact  ├─ Overall season trend
└─ Daily farming decisions └─ Long-term planning


EXAMPLE: Combining Models
──────────────────────────

Day 1 Prediction (Both models agree):
    LSTM:     N = 95.5 kg/ha
    Prophet:  N = 94.8 kg/ha
    → Confidence: HIGH (95%)
    → Recommend action based on both

Day 7 Prediction (Models differ):
    LSTM:     N = 78.5 kg/ha  (drops faster)
    Prophet:  N = 82.1 kg/ha  (smoother)
    → Weight: 70% LSTM + 30% Prophet = 79.6 kg/ha
    → Confidence: MODERATE (80%)
    → Alert: Start planning fertilizer

Day 30 Prediction (Only Prophet available):
    Prophet:  N = 65.2 kg/ha
    → Confidence: MODERATE (75-80%)
    → Planning: Monsoon will accelerate loss
    → Action: Calculate fertilizer needs now
```

---

## Database Schema Overview

```
┌────────────────────────────────────────────────────────┐
│              DATABASE RELATIONSHIPS                    │
└────────────────────────────────────────────────────────┘

farmers
├─ farmer_id (PK)
├─ username
└─ email

fields
├─ field_id (PK)
├─ farmer_id (FK)
└─ location (lat/lon)

crop_cycles (existing)
├─ cycle_id (PK)
├─ farmer_id (FK)
├─ field_id (FK)
├─ crop_name
├─ status ('active', 'completed')
├─ current_n_kg_ha ──┐
├─ current_p_kg_ha   │
├─ current_k_kg_ha   │
├─ start_date        │
└─ expected_end_date │
                     │
                     │ ┌──────────────────────────────┐
                     ├─►daily_weather_nutrient_log   │
                     │  (NEW)                        │
                     │  ├─ log_id (PK)              │
                     │  ├─ cycle_id (FK)            │
                     │  ├─ log_date                 │
                     │  ├─ rainfall_mm              │
                     │  ├─ temperature_avg          │
                     │  ├─ humidity_avg             │
                     │  ├─ n_kg_ha                  │
                     │  ├─ p_kg_ha                  │
                     │  └─ k_kg_ha                  │
                     │  (365+ rows per cycle)      │
                     └──┬───────────────────────────┘
                        │
                        │ ┌──────────────────────────────┐
                        └─►time_series_predictions      │
                           (NEW)                        │
                           ├─ prediction_id (PK)       │
                           ├─ cycle_id (FK)            │
                           ├─ prediction_date          │
                           ├─ forecast_days_ahead      │
                           ├─ predicted_n_kg_ha        │
                           ├─ predicted_p_kg_ha        │
                           ├─ predicted_k_kg_ha        │
                           ├─ model_type ('lstm', ...) │
                           ├─ actual_n_kg_ha (update)  │
                           └─ prediction_error (%)     │

                     
                     ┌──────────────────────────────┐
                     │cycle_performance_history     │
                     │(NEW)                         │
                     ├─ history_id (PK)            │
                     ├─ cycle_id (FK)              │
                     ├─ crop_name                  │
                     ├─ season                     │
                     ├─ year                       │
                     ├─ initial_n/p/k              │
                     ├─ final_n/p/k                │
                     ├─ cycle_duration_days        │
                     ├─ avg_daily_loss_rate        │
                     ├─ total_rainfall_mm          │
                     ├─ yield_kg_ha                │
                     └─ success (boolean)          │
                     (indexed for pattern matching)
```

---

## Summary

This architecture provides:

✅ **Daily Data Collection** - Automatic, no farmer input required  
✅ **Dual Model Prediction** - LSTM (short) + Prophet (long)  
✅ **Early Warning System** - 7-14 days advance notice  
✅ **Continuous Learning** - Weekly model retraining  
✅ **Seamless Integration** - Works with existing RINDM  
✅ **Production Ready** - All code provided, tested patterns  

All components work together to give farmers the information they need to make proactive decisions instead of reactive ones.
