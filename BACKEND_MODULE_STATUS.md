# Backend Module-by-Module Status

## Current Backend Structure

```
backend/
├── app.py                          [ACTIVE] Flask API
├── crop_recommendation.py           [ACTIVE] Main recommendation engine
├── inference.py                     [ACTIVE] Testing/inference script
├── requirements.txt                 [ACTIVE] Dependencies
├── src/
│   ├── data/
│   │   └── preprocess.py           [ACTIVE] Scaling & encoding
│   ├── models/
│   │   ├── ensemble.py             [ACTIVE] Model ensemble
│   │   ├── train_rf.py             [ACTIVE] Random forest training
│   │   ├── train_xgb.py            [ACTIVE] XGBoost training
│   │   ├── train_catboost.py       [ACTIVE] CatBoost training
│   │   ├── train_svm.py            [ACTIVE] SVM training
│   │   └── rindm.py                [❌ MISSING] RINDM model
│   └── utils/
│       ├── crop_database.py        [PARTIAL] Needs nutrient & soil data
│       ├── weather_fetcher.py      [ACTIVE] OpenWeatherMap integration
│       ├── metrics.py              [ACTIVE] Model metrics
│       └── nutrient_calculator.py  [❌ MISSING] Post-harvest calculations
```

---

## Module Status & Required Changes

### ✅ ACTIVE MODULES (No changes needed)

#### 1. [app.py](backend/app.py)
**Status**: Fully functional for Phase 1
- `POST /health` - Health check
- `POST /recommend-crop` - Main crop recommendation endpoint
- `GET /crop-info/<crop_name>` - Crop information retrieval

**What it does right**:
- ✅ Accepts N, P, K, pH, latitude, longitude
- ✅ Fetches weather internally
- ✅ Runs ensemble inference
- ✅ Returns crop + confidence

**TODO**: Add Phase 2 endpoint
- [ ] Add `POST /calculate-post-harvest-nutrients` endpoint

---

#### 2. [crop_recommendation.py](backend/crop_recommendation.py)
**Status**: Working as core recommendation engine
**Class**: `FarmerCropRecommender`

**Current methods**:
- `recommend()` - Returns single crop prediction with confidence

**No changes needed** for current functionality, but could enhance with:
- [ ] `get_top_recommendations()` method for multiple crop options
- [ ] Confidence threshold filtering

---

#### 3. [inference.py](backend/inference.py)
**Status**: Used for testing and manual crop prediction
**Main function**: `predict_crop(N, P, K, temperature, humidity, ph, rainfall)`

**Works well for**:
- Testing predictions locally
- Interactive testing
- Batch prediction scripts

**No changes needed** - Can keep as is for testing

---

#### 4. [src/data/preprocess.py](backend/src/data/preprocess.py)
**Status**: Loads scalers and label encoders trained on the model

**Handles**:
- StandardScaler for numerical features
- LabelEncoder for crop classes
- Correct feature ordering

**No changes needed** for Phase 1, but may need:
- [ ] Enhancement for nutrient value normalization (if needed for RINDM input)

---

#### 5. [src/models/ensemble.py](backend/src/models/ensemble.py)
**Status**: Soft voting ensemble (4 models)
**Models**: Random Forest, XGBoost, CatBoost, SVM

**No changes needed** - Works perfectly for crop recommendation

---

#### 6. [src/utils/weather_fetcher.py](backend/src/utils/weather_fetcher.py)
**Status**: Fetches real-time weather from OpenWeatherMap

**Classes**:
- `WeatherAPIFetcher` - Current weather and forecasts
- `WeatherDataFetcher` - Crop-aware duration weather

**Enhancement needed**:
- [ ] Add `get_historical_rainfall()` method for past season data
- [ ] Add date range parameters
- [ ] Alternative data source fallback

---

### 🟡 PARTIAL MODULES (Needs enhancement)

#### 7. [src/utils/crop_database.py](backend/src/utils/crop_database.py)
**Status**: Has basic crop info
**Currently contains**:
- `CROP_CYCLE_DURATION` - Growing period (days)
- `CROP_SEASON` - Planting season
- `CROP_WATER_REQUIREMENT` - Water needs (mm/year)
- `CROP_OPTIMAL_TEMP` - Temperature ranges

**Missing data structures** (CRITICAL):
```python
# MISSING: Nutrient uptake by crop
CROP_NUTRIENT_UPTAKE = {
    'rice': {'N': 60-80, 'P': 20-30, 'K': 40-60},
    'maize': {'N': 120-150, 'P': 30-40, 'K': 100-150},
    # ... per crop in kg/hectare
}

# MISSING: Soil type leaching behavior
SOIL_LEACHING_COEFFICIENTS = {
    'sandy': {'N': 0.80, 'P': 0.30, 'K': 0.60},
    'loamy': {'N': 0.50, 'P': 0.20, 'K': 0.40},
    'clay': {'N': 0.20, 'P': 0.10, 'K': 0.15},
}
```

**Helper functions to add**:
```python
def get_crop_nutrient_uptake(crop_name)
def get_soil_leaching_coefficient(soil_type, nutrient_type)
def get_nutrient_uptake_range(crop_name)
```

---

### ❌ MISSING MODULES (Need to create)

#### 8. [src/models/rindm.py](backend/src/models/rindm.py) - NEW FILE
**Status**: ❌ DOES NOT EXIST
**Purpose**: Rainfall Induced Nutrient Depletion Model

**Required class**:
```python
class RainfallInducedNutrientDepletionModel:
    def calculate_nutrient_loss(self, rainfall_mm, soil_type, nutrient_type):
        """Calculate nutrient loss for single rainfall event"""
        pass
    
    def calculate_season_losses(self, rainfall_data, soil_type, crop):
        """Aggregate losses over entire season"""
        pass
    
    def get_leaching_impact(self, rainfall_mm, soil_type):
        """Return N, P, K loss percentages"""
        pass
```

**Implementation notes**:
- Uses SOIL_LEACHING_COEFFICIENTS from crop_database.py
- Formula basis: Loss = Rainfall × Leaching_Coeff × Soil_Factor
- Must account for:
  - Different rainfall intensities
  - Soil types (sandy/loamy/clay)
  - Nutrient mobility (N more mobile than K)

---

#### 9. [src/utils/nutrient_calculator.py](backend/src/utils/nutrient_calculator.py) - NEW FILE
**Status**: ❌ DOES NOT EXIST
**Purpose**: Post-harvest nutrient balance calculations

**Required class**:
```python
class PostHarvestNutrientCalculator:
    def calculate_remaining_nutrients(self,
                                     crop_name,
                                     initial_nutrients,
                                     rainfall_data,
                                     soil_type,
                                     harvest_date):
        """Main calculation: Final = Initial - Uptake - Rainfall_Loss"""
        pass
    
    def generate_balance_sheet(self, ...):
        """Detailed report of all changes"""
        pass
    
    def get_nutrient_status(self, final_nutrients):
        """Classify as Low/Medium/High"""
        pass
    
    def get_recommendations(self, final_nutrients):
        """Suggest next crop based on remaining nutrients"""
        pass
```

---

## Dependencies Status

**File**: [requirements.txt](backend/requirements.txt)

**Current packages**:
```
scikit-learn         ✅ (for preprocessing & models)
xgboost             ✅ (base model)
numpy               ✅ (numerical)
pandas              ✅ (data handling)
flask               ✅ (API)
flask-cors          ✅ (cross-origin)
joblib              ✅ (model loading)
catboost            ✅ (base model)
requests            ✅ (weather API calls)
python-dotenv       ✅ (environment vars)
```

**May need to add**:
- [ ] `scipy` - If advanced RINDM statistical calculations needed

---

## Integration Points

### Current Flow (Phase 1):
```
Frontend Request
    ↓ (N, P, K, pH, Lat/Long)
app.py /recommend-crop
    ↓
FarmerCropRecommender.recommend()
    ↓
WeatherAPIFetcher.get_current_weather()
    ├→ OpenWeatherMap API
    └→ Fallback defaults
    ↓
DataPreprocessor.scaler.transform()
    ↓
EnsemblePredictor.predict()
    ↓
Response (crop, confidence)
```

### Required Flow (Phase 2):
```
Frontend Request
    ↓ (crop, initial_nutrients, rainfall_data, soil_type, harvest_date)
app.py /calculate-post-harvest-nutrients
    ↓
PostHarvestNutrientCalculator.calculate_remaining_nutrients()
    ├→ Get CROP_NUTRIENT_UPTAKE
    ├→ RainfallInducedNutrientDepletionModel.calculate_season_losses()
    │   └→ Uses SOIL_LEACHING_COEFFICIENTS
    └→ Calculate Final = Initial - Uptake - Loss
    ↓
Response (balance_sheet, final_nutrients, status)
```

---

## Quick Implementation Guide

### To add Phase 2 support:

1. **Edit** [src/utils/crop_database.py](backend/src/utils/crop_database.py)
   - Add CROP_NUTRIENT_UPTAKE dictionary
   - Add SOIL_LEACHING_COEFFICIENTS dictionary
   - Add helper functions

2. **Create** [src/models/rindm.py](backend/src/models/rindm.py)
   - Implement RainfallInducedNutrientDepletionModel class

3. **Create** [src/utils/nutrient_calculator.py](backend/src/utils/nutrient_calculator.py)
   - Implement PostHarvestNutrientCalculator class

4. **Edit** [app.py](backend/app.py)
   - Add POST /calculate-post-harvest-nutrients endpoint
   - Wire up nutrient calculator

5. **Create** [test_post_harvest.py](backend/test_post_harvest.py)
   - Unit tests for RINDM
   - Integration tests for endpoint
   - Example scenarios

6. **Update** [requirements.txt](backend/requirements.txt) if needed

---

## File Dependencies Map

```
crop_recommendation.py
├── imports: ensemble.py, preprocess.py, crop_database.py, weather_fetcher.py
└── used by: app.py

app.py
├── imports: crop_recommendation.py, weather_fetcher.py, crop_database.py
└── will import: nutrient_calculator.py (new)

src/models/ensemble.py
├── imports: preprocess.py
└── used by: crop_recommendation.py

src/data/preprocess.py
├── loads: scalers, label encoders from disk
└── used by: ensemble.py, crop_recommendation.py

src/utils/crop_database.py
├── data only: CROP_* dictionaries
└── used by: app.py, weather_fetcher.py, [NEW] nutrient_calculator.py, [NEW] rindm.py

src/utils/weather_fetcher.py
├── imports: crop_database.py
└── used by: app.py, crop_recommendation.py

src/models/rindm.py (NEW)
├── imports: crop_database.py
└── used by: nutrient_calculator.py

src/utils/nutrient_calculator.py (NEW)
├── imports: crop_database.py, rindm.py, [maybe] weather_fetcher.py
└── used by: app.py
```

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Fully Working | 6 | ✅ Don't change |
| Needs Enhancement | 1 | 🟡 Add data & methods |
| Missing Entirely | 2 | ❌ Create from scratch |
| Tests Needed | 1 | ❌ Create comprehensive test suite |

